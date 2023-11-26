# 假設 path 是你的字符串
qwe = 'werwer/sdfsdfs/runs/detect/sfksf/sdfsdf.sd'
substring_to_remove = 'runs/detect/'

# 使用 replace 方法刪除子字符串
modified_path = qwe.replace(substring_to_remove, '')

# 輸出修改後的字符串
print(modified_path)

"runs\detect\predict13\a9015fd73ac3c13b67dd08317206d7214f60f7b8_1.jpg"
"/runs/detect/predict13/a9015fd73ac3c13b67dd08317206d7214f60f7b8_1.jpg"