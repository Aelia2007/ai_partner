import streamlit as st

#设置页面的配置项
st.set_page_config(
    page_title="streamlit入门",
    page_icon="🧊",
    #布局(centered,None,width)
    layout="wide",
    #控制侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

#大标题
st.title("Streamlit 入门演示")
st.header("Streamlit 一级标题")
st.subheader("Streamlit 二级标题")

#段落文字
st.write("阿斯蒂芬刚回家快乐")
st.write("asdfghjkl")

#图片
st.image("./resources/花花.jpg",width=400)

#音频
#st.audio

#视频
st.video("./resources/屏幕录制.mp4")

#logo
st.logo("./resources/花花.jpg")

#表格
student_data={
    "name":["张三","李四","王麻子"],
    "age":[20,21,22],
    "gender":["男","女","男"],
    "grade":["100","99","98"]
}
st.table(student_data)

#输入框
#普通输入框
name=st.text_input("请输入姓名：")
st.write(f"您输入的姓名为：{name}")

#密码输入框
password=st.text_input("请输入密码：",type="password")
st.write(f"您输入的密码为：{password}")

#单选按钮
gender=st.radio("请输入您的性别：",["男","女","未知"],index=1)
st.write(f"您的性别为：{gender}")