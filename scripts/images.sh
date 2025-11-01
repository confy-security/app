#!/usr/bin/env bash

set -e -u

image_source=${1:-arkon.png}
image_target=${2:-tasker}
image_folder=${3:-.}

echo "### master image: $image_source"
echo "### image prefix: $image_target"
echo "### image folder: $image_folder"

# 
hash convert ||  { echo "missing imagemagick/convert" ; exit 1 ; }
hash png2icns ||  { echo "missing libicns/png2icns" ; exit 1 ; }
[ -f ${image_source} ] ||  { echo "missing image_source: ${image_source}" ; exit 1 ; }

[ -d ${image_folder} ] || mkdir -p ${image_folder}

#
proper_spec_list=(
   "24x1" "48x1" "64x1" "96x1" "128x1"
   "20x1" "20x2" "20x3"
   "29x1" "29x2" "29x3"
   "40x1" "40x2" "40x3"
   "60x2" "60x3"
   "76x1" "76x2"
   "83.5x2" "1024x1"
)

convert_proper() {
    for image_spec in ${proper_spec_list[*]} ; do
       size=${image_spec%x*}
       scale=${image_spec##*x}
       resize=$(bc <<< ${size}*${scale} )
       echo "### apply ${image_source} spec: ${size}x${size}@${scale}"
       convert ${image_source} \
          -resize ${resize}x${resize} \
          -background none \
          -gravity center \
          -extent ${resize}x${resize} \
          -unsharp '1.5x1+0.7+0.02' \
          ${image_folder}/${image_target}-${size}x${size}@${scale}x.png
    done
}


android_spec_list=(
    48 64 72 96 144 192
)

convert_android() {
    convert_android_round
    convert_android_square
}

convert_android_round() {
    file_type="round"
    for image_spec in ${android_spec_list[*]} ; do
       size=${image_spec}
       scale=1
       resize=$(bc <<< ${size}*${scale} )
       corner=$(bc <<< ${size}*0.5 ) # 50%
       file_name="${image_target}-${file_type}-${size}.png"
       file_path="${image_folder}/${file_name}"
       mask_path="${image_folder}/round-mask.png"
       echo "### apply/android spec: ${size}x${size}@${scale} file: $file_name"
       # produce mask
       convert -size ${resize}x${resize} xc:none \
          -draw "roundrectangle 0,0,${resize},${resize},${corner},${corner}" \
          ${mask_path}
       # produce resize with proper square enforcement
       convert ${image_source} \
          -resize ${resize}x${resize} \
          -background none \
          -gravity center \
          -extent ${resize}x${resize} \
          -unsharp '1.5x1+0.7+0.02' \
          ${file_path}
       # produce composite
       convert ${file_path} \
          -matte ${mask_path} \
          -compose DstIn -composite \
          ${file_path}
       # destroy mask
       rm ${mask_path}
    done
}

convert_android_square() {
    file_type="square"
    for image_spec in ${android_spec_list[*]} ; do
       size=${image_spec}
       scale=1
       resize=$(bc <<< ${size}*${scale} )
       file_name="${image_target}-${file_type}-${size}.png"
       file_path="${image_folder}/${file_name}"
       echo "### apply/android spec: ${size}x${size}@${scale} file: $file_name"
       convert ${image_source} \
          -resize ${resize}x${resize} \
          -background none \
          -gravity center \
          -extent ${resize}x${resize} \
          -unsharp '1.5x1+0.7+0.02' \
          ${file_path}
    done
}


ios_spec_list=(
    20 29 40 58 60 64 76 80 87 120 152 167 180 1024
)

convert_ios() {
    for image_spec in ${ios_spec_list[*]} ; do
       size=${image_spec}
       scale=1
       resize=$(bc <<< ${size}*${scale} )
       file_name="${image_target}-${size}.png"
       file_path="${image_folder}/${file_name}"
       echo "### apply/ios spec: ${size}x${size}@${scale} file: $file_name"
       convert ${image_source} \
          -resize ${resize}x${resize} \
          -background none \
          -gravity center \
          -extent ${resize}x${resize} \
          -unsharp '1.5x1+0.7+0.02' \
          ${file_path}
    done
}


macos_spec_list=(
    16 32 48 64 128 256 512
)

convert_macos() {
    file_list=""
    for image_spec in ${macos_spec_list[*]} ; do
       size=${image_spec}
       scale=1
       resize=$(bc <<< ${size}*${scale} )
       file_name="${image_target}-${size}.png"
       file_path="${image_folder}/${file_name}"
       echo "### apply/macos spec: ${size}x${size}@${scale} file: $file_name"
       convert ${image_source} \
          -resize ${resize}x${resize} \
          -background none \
          -gravity center \
          -extent ${resize}x${resize} \
          -unsharp '1.5x1+0.7+0.02' \
          ${file_path}
       file_list="${file_list} ${file_path}"
    done
    png2icns "${image_target}.icns" ${file_list[@]}
}


windows_spec_list="16,24,32,48,64,72,96,128,256"

convert_windows() {
    echo "### apply/windows spec: ${windows_spec_list}"
    convert ${image_source} \
        -background transparent \
        -define icon:auto-resize=${windows_spec_list} \
        "${image_folder}/${image_target}.ico"
}

convert_default() {
    size="256"
    echo "### apply/default size: ${size}"
    src="${image_target}-256.png"
    dst="${image_target}.png"
    cp ${src} ${dst}  
}


convert_android

convert_ios

convert_macos

convert_windows

convert_default