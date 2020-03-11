#common
imgW = 1024
imgH = 64
alphabet_path = 'classifier_CRNN/data/char_246'

#train
train_dir='/data/train_data_30k_8Mar_new'
pretrained='outputs/train_2020-02-29_11-31/AICR_ocr_dataset_mod_32.pth'
#pretrained=''
gpu_train = '0'  #'0,1' or None
base_lr = 0.0005
max_epoches = 200
workers_train = 8
batch_size = 64
ckpt_prefix = 'AICR_finetune_add_square_box'

#test
test_dir='/home/aicr/cuongnd/text_recognition/data/handwriting/hokhau'
test_dir='/home/aicr/cuongnd/text_recognition/data/handwriting/vib_id'
pretrained_test='classifier_CRNN/ckpt/AICR_finetune_new_data_44_loss_7.266_cer_0.028.pth'  #to test NLP
label = False
test_list=''

gpu_test = '0'
gpu_test = None
workers_test=16
batch_size_test= 1
debug = False
if debug:
    batch_size_test=1