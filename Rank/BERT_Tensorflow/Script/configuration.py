import os
curPath = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(curPath, "../Data")
bert_config_file = os.path.join(curPath, "../Base_Model/version1/bert_config.json")
vocab_file = os.path.join(curPath, "../Base_Model/version1/vocab.txt")
output_dir = os.path.join(curPath, "../Output_Model")
init_checkpoint = os.path.join(curPath, "../Base_Model/version1/bert_model.ckpt",)
