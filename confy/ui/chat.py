"""Graphical chat interface with end-to-end encryption using PySide6."""

import asyncio
import base64

import websockets
from confy_addons import (
    AESEncryption,
    RSAEncryption,
    RSAPublicEncryption,
    deserialize_public_key,
)
from confy_addons.prefixes import AES_KEY_PREFIX, AES_PREFIX, KEY_EXCHANGE_PREFIX, SYSTEM_PREFIX
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from confy.core.constants import RAW_PAYLOAD_LENGTH
from confy.utils import get_protocol, is_prefix


class WebSocketThread(QThread):
    """Separate thread to manage WebSocket communication with end-to-end encryption.

    This class implements a secure chat system using:
    1. Exchange of RSA public keys between users
    2. Generation and secure sharing of symmetric AES key
    3. Encryption of all messages using AES-256

    The handshake protocol works as follows:
    - Both users generate RSA key pairs and exchange public keys
    - The user with "larger" ID generates an AES key and sends it encrypted with RSA
    - All subsequent messages are encrypted with AES
    """

    # === QT SIGNALS FOR THREAD-SAFE COMMUNICATION ===
    message_received = Signal(str, str)  # (sender, message) - Decrypted message received
    connection_status = Signal(str)  # WebSocket connection status (Connected/Disconnected)
    system_message = Signal(str)  # System/server messages
    error_occurred = Signal(str)  # Error notification to display in UI

    def __init__(self, server_address, user_id, recipient_id):
        """Initialize the WebSocket thread with connection and encryption parameters.

        Args:
            server_address (str): WebSocket server address (ex: "ws://localhost:8000")
            user_id (str): Unique ID of current user
            recipient_id (str): Unique ID of chat recipient

        """
        super().__init__()

        # === CONNECTION CONFIGURATION ===
        self.server_address = server_address
        self.user_id = user_id
        self.recipient_id = recipient_id
        self.running = True  # Flag to control thread main loop
        self.websocket = None  # Active WebSocket connection instance

        # === END-TO-END ENCRYPTION SYSTEM ===
        # <--- MODIFIED: Instantiates RSA class that generates and stores key pair
        self.rsa = RSAEncryption()

        # Keys related to peer (other user in chat)
        self.peer_public_key = None  # RSA public key received from recipient
        self.peer_aes_key = None  # AES-256 shared key for fast encryption

        # Handshake control
        self.public_sent = False  # Flag to prevent duplicate public key sending

        # === ASYNCHRONOUS MESSAGE QUEUE ===
        # Asyncio queue to process outgoing messages in thread-safe manner
        self.message_queue = asyncio.Queue()

    def run(self):
        """Thread entry point - executes asyncio loop.

        This method is called automatically when start() is invoked.
        Creates a new event loop for this thread.
        """
        asyncio.run(self.websocket_client())

    async def websocket_client(self):
        """Main WebSocket client that manages the connection.

        Establishes WebSocket connection, starts asynchronous tasks for:
        - Receiving messages from server
        - Processing message queue for sending

        Raises:
            Exception: WebSocket connection or communication errors

        """
        # Constructs WebSocket URI based on detected protocol
        protocol, host = get_protocol(self.server_address)
        uri = f'{protocol}://{host}/ws/{self.user_id}@{self.recipient_id}'

        try:
            # Establishes WebSocket connection with server
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                self.connection_status.emit('Conectado')

                # === CONCURRENT ASYNCHRONOUS TASKS ===
                # Task 1: Listen for server messages continuously
                receive_task = asyncio.create_task(self.receive_messages())
                # Task 2: Process message queue for sending
                send_task = asyncio.create_task(self.process_send_queue())

                # Waits until one of the tasks completes (connection lost or error)
                done, pending = await asyncio.wait(
                    [receive_task, send_task], return_when=asyncio.FIRST_COMPLETED
                )

                # Cancels tasks still running
                for task in pending:
                    task.cancel()

        except Exception as e:
            # Notifies UI about connection error
            self.error_occurred.emit(f'Erro de conexÃ£o: {str(e)}')
        finally:
            # Always notifies disconnection when finishing
            self.connection_status.emit('Desconectado')

    async def receive_messages(self):
        """Main loop to receive and process WebSocket messages.

        Continuously listens for server messages and processes them
        based on their prefixes (system, public key, AES key, message).

        Raises:
            Exception: Errors during message reception or processing

        """
        try:
            while self.running:
                try:
                    # Receives next WebSocket message (blocking)
                    message = await self.websocket.recv()
                except websockets.ConnectionClosed:
                    # Connection was closed by server or network
                    self.running = False
                    self.connection_status.emit('ConexÃ£o fechada')
                    break

                # Processes message based on its type/prefix
                await self.process_received_message(message)

        except Exception as e:
            self.error_occurred.emit(f'Erro ao receber mensagem: {str(e)}')

    async def process_received_message(self, message):
        """Processes received messages based on their prefixes.

        The system uses prefixes to identify message types:
        - SYSTEM_PREFIX: Server messages (not encrypted)
        - KEY_EXCHANGE_PREFIX: RSA public keys
        - AES_KEY_PREFIX: AES key encrypted with RSA
        - AES_PREFIX: Encrypted chat messages

        Args:
            message (str): Raw message received from WebSocket

        """
        # === SERVER MESSAGES (NOT ENCRYPTED) ===
        if is_prefix(message, SYSTEM_PREFIX):
            # Checks if recipient has connected to initiate handshake
            if message == f'{SYSTEM_PREFIX} O usuÃ¡rio destinatÃ¡rio agora estÃ¡ conectado.':
                # Sends public key automatically (only once)
                if not self.public_sent:
                    # <--- MODIFIED: Uses instance property 'rsa'
                    await self.websocket.send(f'{KEY_EXCHANGE_PREFIX}{self.rsa.base64_public_key}')
                    self.public_sent = True
            # Forwards system message to UI
            self.system_message.emit(message)
            return

        # === RECEIVES RSA PUBLIC KEY FROM PEER ===
        elif is_prefix(message, KEY_EXCHANGE_PREFIX):
            # Extracts public key from message (removes prefix)
            b64_key = message[len(KEY_EXCHANGE_PREFIX) :]
            try:
                # Deserializes public key from base64
                self.peer_public_key = deserialize_public_key(b64_key)
            except Exception as e:
                self.error_occurred.emit(f'Chave pÃºblica do peer invÃ¡lida: {e}')
                return

            # Responds with our public key if we haven't sent it yet
            if not self.public_sent:
                try:
                    # <--- MODIFIED: Uses instance property 'rsa'
                    await self.websocket.send(f'{KEY_EXCHANGE_PREFIX}{self.rsa.base64_public_key}')
                    self.public_sent = True
                except Exception as e:
                    self.error_occurred.emit(f'Falha ao enviar chave pÃºblica: {e}')
                    return

            # === AES KEY GENERATION LOGIC ===
            # Only one user should generate the AES key to avoid conflicts
            # Criterion: user with "larger" ID lexicographically generates the key
            if self.peer_aes_key is None and self.public_sent:
                should_generate = str(self.user_id) > str(self.recipient_id)
                if should_generate:
                    # <--- MODIFIED: Instantiates AESEncryption to generate the key
                    aes = AESEncryption()
                    # <--- MODIFIED: Instantiates RSAPublicEncryption to encrypt
                    encrypted_key = RSAPublicEncryption(self.peer_public_key).encrypt(aes.key)
                    # Encodes in base64 for transmission
                    b64_encrypted_key = base64.b64encode(encrypted_key).decode()
                    await self.websocket.send(f'{AES_KEY_PREFIX}{b64_encrypted_key}')
                    # Stores generated key for local use
                    self.peer_aes_key = aes.key

        # === RECEIVES ENCRYPTED AES KEY ===
        elif is_prefix(message, AES_KEY_PREFIX):
            # Extracts encrypted AES key from message
            b64_enc = message[len(AES_KEY_PREFIX) :]
            try:
                # Decodes from base64
                encrypted_key = base64.b64decode(b64_enc)
                # <--- MODIFIED: Uses method from instance 'rsa'
                # Stores AES key for message encryption
                self.peer_aes_key = self.rsa.decrypt(encrypted_key)
                self.system_message.emit('Chave AES estabelecida - comunicaÃ§Ã£o segura ativa')
            except Exception as e:
                self.error_occurred.emit(f'Falha ao descriptografar a chave AES: {e}')
            return

        # === MESSAGE ENCRYPTED WITH AES ===
        elif is_prefix(message, AES_PREFIX):
            # Checks if handshake was completed
            if self.peer_aes_key is None:
                self.system_message.emit(
                    'Mensagem criptografada recebida, mas chave AES nÃ£o definida'
                )
                return

            # <--- START OF SIGNATURE VERIFICATION LOGIC --->
            raw_payload_with_sig = message[len(AES_PREFIX) :]
            try:
                # 1. Separates payload and signature
                parts = raw_payload_with_sig.split('::')
                if len(parts) != RAW_PAYLOAD_LENGTH:
                    self.error_occurred.emit('Payload de mensagem malformado recebido.')
                    return
                b64_payload, b64_signature = parts

                # 2. Decrypts the message
                decrypted_message = AESEncryption(self.peer_aes_key).decrypt(b64_payload)

                # 3. Prepares data for verification
                decrypted_bytes = decrypted_message.encode('utf-8')
                signature_bytes = base64.b64decode(b64_signature)

                # 4. VERIFIES the signature
                RSAPublicEncryption(self.peer_public_key).verify(decrypted_bytes, signature_bytes)

                # 5. SUCCESS: Emits the decrypted and verified message
                self.message_received.emit(self.recipient_id, decrypted_message)

            except Exception as e:
                # 7. GENERAL FAILURE: Decryption error, base64, etc.
                self.error_occurred.emit(f'Falha ao descriptografar/verificar mensagem: {e}')
            # <--- END OF SIGNATURE VERIFICATION LOGIC --->
        else:
            # === PLAIN TEXT MESSAGE (FALLBACK) ===
            # For compatibility or debugging - not recommended in production
            self.message_received.emit(self.recipient_id, message)

    async def process_send_queue(self):
        """Continuously processes the message queue for sending.

        Infinite loop that gets messages from the queue and sends them encrypted.
        Uses timeout to allow periodic checking of self.running flag.

        Raises:
            Exception: Errors during message sending

        """
        while self.running:
            try:
                # Waits for message in queue (1 second timeout)
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                # Encrypts and sends the message
                await self.send_encrypted_and_signed_message(message)
            except TimeoutError:
                # Normal timeout - continues loop
                continue
            except Exception as e:
                self.error_occurred.emit(f'Erro ao enviar mensagem: {str(e)}')

    async def send_encrypted_and_signed_message(self, message):
        """Encrypts AND SIGNS a message before sending via WebSocket."""
        if self.peer_aes_key:
            try:
                # <--- START OF SIGNATURE LOGIC --->

                # 1. Encrypts the message with AES
                encrypted_payload = AESEncryption(self.peer_aes_key).encrypt(message)

                # 2. Signs the ORIGINAL message (in bytes) with our private key
                message_bytes = message.encode('utf-8')
                signature = self.rsa.sign(message_bytes)  # Uses instance 'rsa'

                # 3. Encodes signature in base64
                b64_signature = base64.b64encode(signature).decode('utf-8')

                # 4. Combines and sends
                final_payload = f'{AES_PREFIX}{encrypted_payload}::{b64_signature}'
                await self.websocket.send(final_payload)

                # <--- END OF SIGNATURE LOGIC --->
            except Exception as e:
                self.error_occurred.emit(f'Falha ao criptografar/assinar/enviar: {e}')
        else:
            self.system_message.emit('Chave AES ainda nÃ£o estabelecida. Aguarde o handshake.')

    def send_message(self, message):
        """Adds message to send queue in thread-safe manner.

        This method is called from the UI thread and needs to be thread-safe
        to communicate with the asyncio thread.

        Args:
            message (str): Message to be sent

        Note:
            Uses different strategies for compatibility between asyncio versions.

        """
        if self.running:
            # === STRATEGY 1: Create new temporary loop ===
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.message_queue.put(message))
                loop.close()
            except Exception:
                # === STRATEGY 2: Use existing loop (fallback) ===
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.message_queue.put(message), asyncio.get_event_loop()
                    )
                except Exception as e:
                    # If all strategies fail, notifies error
                    self.error_occurred.emit(f'Erro ao enfileirar mensagem: {str(e)}')

    def stop(self):
        """Stops the WebSocket thread safely.

        Sets stop flag and waits for thread completion.
        Should be called before closing the application.
        """
        self.running = False  # Signals loops to stop
        self.quit()  # Finalizes the Qt thread
        self.wait()  # Waits for thread to complete


class ChatWindow(QWidget):
    """Main chat window with graphical interface using PySide6.

    Provides a complete user interface for:
    - Viewing chat messages in real time
    - Sending encrypted messages
    - Monitoring connection and system status
    - Displaying errors and notifications

    Server communication is managed by WebSocketThread.
    """

    def __init__(self, username=None, recipient=None, server_address=None):
        """Initializes the chat window with optional parameters.

        Args:
            username (str, optional): Current user's name
            recipient (str, optional): Recipient's name
            server_address (str, optional): WebSocket server address

        """
        super().__init__()

        # === CONFIGURATION PARAMETERS ===
        self.username = username
        self.recipient = recipient
        self.server_address = server_address

        # === UI ELEMENTS ===
        self.messages_area = None  # Text area for displaying messages
        self.send_button = None  # Button to send messages
        self.message_input = None  # Input field for typing messages

        # Sets window title with recipient's name
        self.setWindowTitle(f'Confy - Chat com {self.recipient}')

        # Builds the graphical interface
        self.setup_ui()

        # === CONNECTION MANAGEMENT ===
        self.websocket_thread = None  # WebSocket communication thread
        self.connection_status = 'Desconectado'  # Current connection status

        # Connects automatically if all parameters were provided
        if all([username, recipient, server_address]):
            self.connect_to_server()

    def setup_ui(self):
        """Configures all user interface elements.

        Creates layout with:
        - Message display area (read-only)
        - Input field for new messages
        - Send button

        Applies custom CSS styles for dark theme.
        """
        # === MAIN VERTICAL LAYOUT ===
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)  # Spacing between elements

        # === MESSAGE AREA ===
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)  # View only, not editable
        # CSS style for dark theme with rounded borders
        self.messages_area.setStyleSheet(
            """
            QTextEdit {
                border: 1.3px solid #393939;
                border-radius: 10px;
                color: white;
                padding: 8px;
                background-color: #202020;
            }
            """
        )
        layout.addWidget(self.messages_area)

        # === MESSAGE SENDING AREA ===
        send_layout = QHBoxLayout()

        # Input field for typing
        self.message_input = QLineEdit(placeholderText='Mensagem')
        self.message_input.setFixedHeight(40)
        self.message_input.setStyleSheet(
            """
            QLineEdit {
                border: 1.3px solid #393939;
                border-radius: 10px;
                color: white;
                padding: 8px;
                background-color: #303030;
            }
            """
        )
        # Connects Enter/Return to send message
        self.message_input.returnPressed.connect(self.send_message)

        # Send button
        self.send_button = QPushButton('Enviar')
        self.send_button.setFixedSize(60, 40)
        self.send_button.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                color: black;
                border-radius: 10px;
            }

            QPushButton:hover {
                background-color: #C0C0C0;
            }

            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
            """
        )
        # Connects button click to send message
        self.send_button.clicked.connect(self.send_message)

        # Adds input and button to horizontal layout
        send_layout.addWidget(self.message_input)
        send_layout.addWidget(self.send_button)

        # Adds sending area to main layout
        layout.addLayout(send_layout)
        self.setLayout(layout)

        # === INITIAL CONFIGURATION ===
        # Disables controls until connected
        self.update_connection_status('Desconectado')

    def connect_to_server(self):
        """Establishes connection with WebSocket server.

        Creates and starts WebSocketThread if one isn't already running.
        Connects all signals for thread-safe communication with UI.
        """
        # Prevents multiple simultaneous connections
        if self.websocket_thread and self.websocket_thread.isRunning():
            return

        # === COMMUNICATION THREAD CREATION ===
        self.websocket_thread = WebSocketThread(self.server_address, self.username, self.recipient)

        # === THREAD-SAFE SIGNAL CONNECTIONS ===
        # Signal: Message received -> Callback to display in UI
        self.websocket_thread.message_received.connect(self.on_message_received)
        # Signal: Connection status -> Update UI and controls
        self.websocket_thread.connection_status.connect(self.on_connection_status)
        # Signal: System message -> Display notification
        self.websocket_thread.system_message.connect(self.on_system_message)
        # Signal: Error occurred -> Show error in UI
        self.websocket_thread.error_occurred.connect(self.on_error_occurred)

        # Starts the thread (calls run() automatically)
        self.websocket_thread.start()

    def send_message(self):
        """Sends message typed by user.

        Performs basic validations, displays the message in UI immediately,
        and sends it via WebSocketThread for encryption and transmission.

        Returns:
            None: Returns early if message is empty or not connected

        """
        # Gets text and removes whitespace
        message = self.message_input.text().strip()
        if not message:
            return  # Doesn't send empty messages

        # Checks if connection is active
        if not self.websocket_thread or not self.websocket_thread.isRunning():
            self.show_error('NÃ£o conectado ao servidor')
            return

        # === DISPLAYS MESSAGE IMMEDIATELY IN UI ===
        # Shows message as "own" (green color)
        self.add_message_to_chat('VocÃª', message, is_own=True)

        # === SENDS VIA WEBSOCKET ===
        # Adds to send queue of thread (thread-safe)
        self.websocket_thread.send_message(message)

        # Clears input field for next message
        self.message_input.clear()

    def on_message_received(self, sender, message):
        """Callback executed when message is received from thread.

        Args:
            sender (str): ID of message sender
            message (str): Message content already decrypted

        """
        # Adds received message to chat area (blue color)
        self.add_message_to_chat(sender, message, is_own=False)

    def on_connection_status(self, status):
        """Callback for WebSocket connection status changes.

        Args:
            status (str): New status ('Conectado', 'Desconectado', etc.)

        """
        self.update_connection_status(status)

    def on_system_message(self, message):
        """Callback for system/server messages.

        Args:
            message (str): System message to be displayed

        """
        self.add_system_message(message)

    def on_error_occurred(self, error):
        """Callback for error notifications from thread.

        Args:
            error (str): Description of error that occurred

        """
        self.show_error(error)

    def add_message_to_chat(self, sender, message, is_own=False):
        """Add formatted message to chat area.

        Args:
            sender (str): Name of sender
            message (str): Message content
            is_own (bool): True if own message, False if received

        Note:
            Uses HTML for formatting with different colors:
            - Green (#4CAF50): Own messages
            - Blue (#2196F3): Received messages

        """
        if is_own:
            # Own message - name in green
            formatted_message = (
                f'<div style="color: #4CAF50; font-weight: bold;">'
                f'{sender}: '
                f'<span style="color: white; font-weight: normal;">{message}</span>'
                f'</div>'
            )
        else:
            # Received message - name in blue
            formatted_message = (
                f'<div style="color: #2196F3; font-weight: bold;">'
                f'{sender}: '
                f'<span style="color: white; font-weight: normal;">{message}</span>'
                f'</div>'
            )

        # Adds formatted HTML to message area
        self.messages_area.append(formatted_message)

    def add_system_message(self, message):
        """Add system message with special formatting.

        Args:
            message (str): System/server message

        Note:
            System messages appear in yellow and italic.

        """
        formatted_message = (
            f'<div style="color: #FFC107; font-style: italic;">Sistema: {message}</div>'
        )
        self.messages_area.append(formatted_message)

    def update_connection_status(self, status):
        """Update connection status and controls enabling.

        Args:
            status (str): New connection status

        Note:
            - 'Conectado': Enables send controls
            - Others: Disables controls and shows status

        """
        self.connection_status = status

        if status == 'Conectado':
            # Enables controls for sending messages
            self.send_button.setEnabled(True)
            self.message_input.setEnabled(True)
            self.add_system_message('Conectado ao servidor')
        else:
            # Disables controls when disconnected
            self.send_button.setEnabled(False)
            # Only shows status if not normal disconnection
            if status != 'Desconectado':
                self.add_system_message(f'Status: {status}')

    def show_error(self, error):
        """Display error message in chat area.

        Args:
            error (str): Error description to be displayed

        """
        self.add_system_message(f'Erro: {error}')

    def closeEvent(self, event):
        """Cleanup executed when window is being closed.

        Ensures that the WebSocket thread is finalized properly
        to prevent resource leaks or orphaned threads.

        Args:
            event (QCloseEvent): Window close event

        """
        # Stops WebSocket thread if running
        if self.websocket_thread and self.websocket_thread.isRunning():
            self.websocket_thread.stop()

        # Accepts the close event
        event.accept()
