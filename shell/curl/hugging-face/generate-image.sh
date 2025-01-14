# INFO
# SD 3.5 Large model: https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large
# FLUX: https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev

###########################################################
# INPUTS
MODEL_URL="https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"
BEARER_TOKEN="hf_TOKEN"
INPUT_FILE="input.jpg"
OUTPUT_FILE="output.png"
OUTPUT_FILE_WIDTH=512
OUTPUT_FILE_HEIGHT=512
SEED=0
STEPS=20
PROMPT="Cowboy riding a horse. The background should have a sky color same as the input image."
NEGATIVE_PROMPT="Tail"

## OVERRIDE INPUTS VIA CLI ARGS
while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$package - utility to query a model using Hugging Face's Inference API."
      echo " "
      echo "options:"
      echo "-h, --help                            show this help message"
      echo "-m, --model=URL                       the api-inference.huggingface.co URL from the model card->view code page."
      echo "-t, --token=TOKEN                     the bearer token from the HF account being used."
      echo "-i, --image-file=IMAGE_LOCATION       the location of the image on the machine running this script."
      echo "-o, --output-file=IMAGE_LOCATION      the location where the output will be stored."
      echo "-ow, --output-width=INT               the width of the output image in number of pixels."
      echo "-oh, --output-height=INT              the height of the output image in number of pixels."
      echo "-s, --seed=INT                        the seed supplied to the prompt."
      echo "-st, --steps=INT                      the number of inference steps to denoise the image."
      echo "-p, --prompt="Prompt text"            the text for the prompt, envase it with quotes."
      echo "-n, --negative-prompt="Prompt text"  the text for the negative prompt, envase it with quotes."
      exit 0
      ;;
    -m)
      shift
      if test $# -gt 0; then
        MODEL_URL=$1
        echo "Model URL: $MODEL_URL"
      else
        echo "No Model URL specified. Using default Model URL: $MODEL_URL"
        break
      fi
      shift
      ;;
    --model*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        MODEL_URL=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Model URL: $MODEL_URL"
      else
        echo "No Model URL specified. Using default Bearer Token: $MODEL_URL"
        break
      fi
      shift
      ;;
    -t)
      shift
      if test $# -gt 0; then
        BEARER_TOKEN=$1
        echo "Bearer Token: $BEARER_TOKEN"
      else
        echo "No Bearer Token specified. Using default Bearer Token: $BEARER_TOKEN"
        break
      fi
      shift
      ;;
    --token*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        BEARER_TOKEN=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Bearer Token: $BEARER_TOKEN"
      else
        echo "No Bearer Token specified. Using default Bearer Token: $BEARER_TOKEN"
        break
      fi
      shift
      ;;
    -i)
      shift
      if test $# -gt 0; then
        INPUT_FILE=$1
        echo "Input File: $INPUT_FILE"
      else
        echo "No Input File specified, hence no Input Image will be used."
        break
      fi
      shift
      ;;
    --input-file*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        INPUT_FILE=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Input File: $INPUT_FILE"
      else
        echo "No Input File specified, hence no Input Image will be used."
        break
      fi
      shift
      ;;
    -o)
      shift
      if test $# -gt 0; then
        OUTPUT_FILE=$1
        echo "Output File: $OUTPUT_FILE"
      else
        echo "No Output File specified, default Output File location will be used: $OUTPUT_FILE"
        break
      fi
      shift
      ;;
    --output-file*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        OUTPUT_FILE=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Output File: $OUTPUT_FILE"
      else
        echo "No Output File specified, default Output File location will be used: $OUTPUT_FILE"
        break
      fi
      shift
      ;;
    -ow)
      shift
      if test $# -gt 0; then
        OUTPUT_FILE_WIDTH=$1
        echo "Output File Width: $OUTPUT_FILE_WIDTH"
      else
        echo "No Output File Width specified, default Output File Width will be used: $OUTPUT_FILE_WIDTH"
        break
      fi
      shift
      ;;
    --output-file-width*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        OUTPUT_FILE_WIDTH=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Output File Width: $OUTPUT_FILE_WIDTH"
      else
        echo "No Output File Width specified, default Output File Width will be used: $OUTPUT_FILE_WIDTH"
        break
      fi
      shift
      ;;
    -oh)
      shift
      if test $# -gt 0; then
        OUTPUT_FILE_HEIGHT=$1
        echo "Output File Height: $OUTPUT_FILE_HEIGHT"
      else
        echo "No Output File Height specified, default Output File Height will be used: $OUTPUT_FILE_HEIGHT"
        break
      fi
      shift
      ;;
    --output-file-height*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        OUTPUT_FILE_HEIGHT=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Output File Height: $OUTPUT_FILE_HEIGHT"
      else
        echo "No Output File Height specified, default Output File Height will be used: $OUTPUT_FILE_HEIGHT"
        break
      fi
      shift
      ;;
    -s)
      shift
      if test $# -gt 0; then
        SEED=$1
        echo "Seed: $SEED"
      else
        echo "No Seed specified, default Seed will be used: $SEED"
        break
      fi
      shift
      ;;
    --seed*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        SEED=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Seed: $SEED"
      else
        echo "No Seed specified, default Seed will be used: $SEED"
        break
      fi
      shift
      ;;
    -st)
      shift
      if test $# -gt 0; then
        STEPS=$1
        echo "Steps: $STEPS"
      else
        echo "No Steps specified, default Steps will be used: $STEPS"
        break
      fi
      shift
      ;;
    --steps*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        STEPS=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Steps: $STEPS"
      else
        echo "No Steps specified, default Steps will be used: $STEPS"
        break
      fi
      shift
      ;;
    -p)
      shift
      if test $# -gt 0; then
        PROMPT=$1
        echo "Prompt: $PROMPT"
      else
        echo "No Prompt specified. Using default Prompt: $PROMPT"
        break
      fi
      shift
      ;;
    --prompt*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        PROMPT=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Prompt: $PROMPT"
      else
        echo "No Prompt specified. Using default Prompt: $PROMPT"
        break
      fi
      shift
      ;;
    -n)
      shift
      if test $# -gt 0; then
        NEGATIVE_PROMPT=$1
        echo "Negative Prompt: $NEGATIVE_PROMPT"
      else
        echo "No Negative Prompt specified. Using default Negative Prompt: $NEGATIVE_PROMPT"
        break
      fi
      shift
      ;;
    --negative-prompt*)
      if [[ `echo $1 | sed -e 's/^[^=]*=//g'` != "" ]]; then
        NEGATIVE_PROMPT=`echo $1 | sed -e 's/^[^=]*=//g'`
        echo "Negative Prompt: $NEGATIVE_PROMPT"
      else
        echo "No Negative Prompt specified. Using default Negative Prompt: $NEGATIVE_PROMPT"
        break
      fi
      shift
      ;;
    *)
      break
      ;;
  esac
done

## VALIDATE INPUTS
if [[ -n $INPUT_FILE && ! -f "$INPUT_FILE" ]];then
  echo "Error: Couldn't read from input image at $INPUT_FILE."
  exit 1
fi
if ! command -v base64 2>&1 >/dev/null
then
    echo "base64 could not be found. Please install base64."
    exit 1
fi
if ! command -v curl 2>&1 >/dev/null
then
    echo "curl could not be found. Please install curl."
    exit 1
fi

## SHOW INPUTS TO USER
echo "Using the following inputs:"
echo "Model URL = $MODEL_URL
Token = $BEARER_TOKEN
Input file = $INPUT_FILE
Output file = $OUTPUT_FILE
Output file width = $OUTPUT_FILE_WIDTH
Output file height = $OUTPUT_FILE_HEIGHT
Seed = $SEED
Steps = $STEPS
Prompt = $PROMPT
Negative Prompt = $NEGATIVE_PROMPT"

##################################################

# QUERY INFERENCE API
echo "Generating image..."
curl -X POST -H "Content-Type: application/json" $MODEL_URL \
	-H "Authorization: Bearer $BEARER_TOKEN" \
  --data-binary @$INPUT_FILE \
  -d "{
    'inputs': {
        'prompt': '$PROMPT',
        'negative_prompt': '$NEGATIVE_PROMPT',
        'seed': '$SEED',
        'num_inference_steps': '$STEPS',
        'width': '$OUTPUT_FILE_WIDTH',
        'height': '$OUTPUT_FILE_HEIGHT'
    }" \
  -o $OUTPUT_FILE

  # -d "{
  #   'image': 'data:image/jpeg;base64,$(base64 $INPUT_FILE)',
  #   'inputs': {
  #       'prompt': '$PROMPT',
  #       'negative_prompt': '$NEGATIVE_PROMPT',
  #       'seed': '$SEED',
  #       'num_inference_steps': '$STEPS',
  #       'width': '$OUTPUT_FILE_WIDTH',
  #       'height': '$OUTPUT_FILE_HEIGHT'
  #   }" \

  # -F "image=@$INPUT_FILE" \
  # -F "inputs={
  # 'prompt': '$PROMPT',
  # 'negative_prompt': '$NEGATIVE_PROMPT',
  # 'seed': $SEED,
  # 'num_inference_steps': $STEPS,
  # 'width': $OUTPUT_FILE_WIDTH,
  # 'height': $OUTPUT_FILE_HEIGHT
  # }" \