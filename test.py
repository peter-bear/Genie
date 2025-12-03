import time
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.append(src_dir)

import genie_tts as genie

# # Automatically downloads required files on first run
# genie.load_predefined_character('misono_mika')

# genie.tts(
#     character_name='misono_mika',
#     text='这是一个非常长的测试文本，主要目的是为了验证系统是否能够正确地处理长句分割逻辑；如果在处理过程中出现了显存溢出或者报错，那就说明我们需要调整切分的阈值，或者检查标点符号的匹配规则是否正确。',
#     play=True,  # Play the generated audio directly
# )

# time.sleep(20)  # Add delay to ensure audio playback completes

# import genie_tts as genie

# genie.convert_to_onnx(
#     torch_pth_path=r"./models/SV_WutheringWaves_CN_1.3.pth",  # Replace with your .pth file
#     torch_ckpt_path=r"./models/GPT_WutheringWaves_CN_1.3.ckpt",  # Replace with your .ckpt file
#     output_dir=r"./outputs"  # Directory to save ONNX model
# )


# from genie_tts.Chinese.ChineseG2P import chinese_to_phones, ChineseG2P

# if __name__ == "__main__":
#     # 测试长难句
#     text = "你好！虽然目前的语音合成技术准确率已经超过了99%，但在处理‘银行’和‘行走’这种多音字时，或者遇到‘知识’、‘支持’这种整体认读音节时，偶尔还是需要微调的。"
    
#     # 1. 查看分词和注音效果 (可视化)
#     # 调用类的 g2p 方法，直接看拆分后的符号
#     phonemes = ChineseG2P.g2p(text)
#     print(f"【分后的效果】: {phonemes}")

#     # 2. 查看转换后的 ID
#     ids = chinese_to_phones(text)
#     print(f"【结果 ID】:   {ids}")


# Step 1: Load character voice model
genie.load_character(
    character_name='fuxuan',  # Replace with your character name
    onnx_model_dir=r"./outputs",  # Folder containing ONNX model
)

# Step 2: Set reference audio (for emotion and intonation cloning)
genie.set_reference_audio(
    character_name='fuxuan',  # Must match loaded character name
    audio_path=r"./models/reference.wav",  # Path to reference audio
    audio_text="直到每一个信徒都回归“天国”，被彻底同化的地域将在黑云的牵引下开始它的巡礼，前往下一个地点传播“福音”。",  # Corresponding text
)

# Step 3: Run TTS inference and generate audio
genie.tts(
    character_name='fuxuan',  # Must match loaded character
    text="你好！虽然目前的语音合成技术准确率已经超过了99%，但在处理‘银行’和‘行走’这种多音字时，或者遇到‘知识’、‘支持’这种整体认读音节时，偶尔还是需要微调的。",  # Text to synthesize
    play=True,  # Play audio directly
)

time.sleep(20)  