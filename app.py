import streamlit as st
import base64
import os, glob
import platform
sys = platform.system()
work_dir = os.path.dirname(os.path.abspath(__file__))
print(sys)
if sys == "Windows":
    mypath = work_dir + "\\forecast\\fr\\"
else:
    mypath = work_dir + "/forecast/fr/"

print(mypath)
os.chdir(mypath)
fileslist = []
for file in glob.glob("*.gif"):
    print(file)
    fileslist.append(file)

print(fileslist)

for i in range(0,len(fileslist)):
    file_ = open(mypath + fileslist[i], "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
        unsafe_allow_html=True,
    )