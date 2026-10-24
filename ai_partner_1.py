import streamlit as st
import os
from openai import OpenAI
from streamlit import session_state
from datetime import datetime
import json

#设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

#生成会话标识的函数
def generate_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#保存会话信息的函数
def save_session():
    # 1.保存当前会话信息
    if st.session_state.current_session:

        # 构建新的会话对象
        session_data = {
            "nickname": session_state.nickname,
            "character": session_state.character,
            "current_session": session_state.current_session,
            "messages": session_state.messages
        }

        # 如果 sessions 目录不存在，则创建 sessions
        if not os.path.exists("sessions"):
            os.makedirs("sessions")

        # 保存会话数据
        with open(f"sessions/{session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)


#初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages =[]

#加载所有的会话列表
def load_sessions():
    sessions = []
    if os.path.exists("sessions"):
        for filename in os.listdir("sessions"):
            if filename.endswith(".json"):
                sessions.append(filename[:-5])#（字符串切片）：在 Python 中，-5 表示从字符串的倒数第 5 个字符开始往前截取。
                sessions.sort(reverse=True)
    return sessions

#加载指定的会话信息
def load_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            # 读取会话数据
            with open(f"sessions/{session_id}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]#Streamlit 的 session_state 是内存中的，页面刷新后就没了
                st.session_state.nickname = session_data["nickname"]
                st.session_state.character = session_data["character"]
                st.session_state.current_session = session_id

    except FileNotFoundError:
        st.error("会话不存在")

#删除会话信息
def delete_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            os.remove(f"sessions/{session_id}.json")
            #如果删除的是当前会话，需要更新消息列表
            if session_id == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_id()

    except Exception:
        st.error("删除会话失败！")


# 大标题
st.title("AI智能伴侣")

# logo
st.logo("./resources/花花.jpg")

# 创建OpenAI客户端
# 优先从 secrets 读取（云端部署），否则从环境变量读取（本地开发）
api_key = st.secrets.get("MOONSHOT_API_KEY") if hasattr(st, 'secrets') and "MOONSHOT_API_KEY" in st.secrets else os.environ.get("MOONSHOT_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.moonshot.cn/v1"
)


def agent_loop(user_message: str):
    """简化版 agent loop，不调用任何工具，直接对话。"""

    messages = [
        {"role": "system", "content":"""
                你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。：
                规则：
                1．每次只回1条消息
                2．禁止任何场景或状态描述性文字
                3．匹配用户的语言
                4．回复简短，像微信聊天一样
                5．有需要的话可以用❤️🌸等emoji表情
                6．用符合伴侣性格的方式对话
                7．回复的内容，要充分体现伴侣的性格特征

                伴侣性格：
                - %s

                 你必须严格遵守上述规则来回复用户。"""
        %(session_state.nickname, session_state.character)}
    ]

    #保留20轮对话，并过滤掉内容为空的assistant消息（防止400报错）
    history = [msg for msg in st.session_state.messages[-20:] if msg["content"] != ""]
    messages.extend(history)

    # 添加当前用户消息
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="kimi-k2.7-code",
        messages=messages,
        stream=True
    )

    return response#直接返回生成器，不要取 .choices[0].message.content

#昵称
if "nickname" not in session_state:
    session_state.nickname = "花花"

#性格
if "character" not in session_state:
    session_state.character = "活泼开朗的东北姑娘"

#会话标识
if "current_session" not in session_state:
    now=session_state.current_session = generate_session_id()
    session_state.current_session = now

# 显示聊天信息
st.text(f"会话名称：{st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

#会话信息
with st.sidebar:
    st.subheader("AI控制面板")

    #新建会话
    if st.button("新建会话",width="stretch",icon="✍️"):
         #1.保存当前会话信息
         save_session()

         # 2.创建新的会话
         if st.session_state.messages:  # 如果聊天消息非空，True，否则False
           st.session_state.messages = []
           st.session_state.current_session = generate_session_id()
           save_session()
           st.rerun()  # 重新运行当前页面

    #会话历史
    st.text("会话历史")
    sessions = load_sessions()
    for session in sessions:
        col1,col2=st.columns([4,1])
        with col1:
            #加载会话信息
            # 三元运算符：条件为真时执行的值 if 条件 else 条件为假时执行的值
            if st.button(session,width="stretch",icon="📃",type="primary" if session==st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            if st.button("",width="stretch",icon="❌",key=session):
                delete_session(session)
                st.rerun()

    #分隔线
    st.markdown("___")

#伴侣信息 with:streamlit中的上下文管理器
with st.sidebar:
    st.subheader("伴侣信息")
    nickname=st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nickname)
    if nickname:
        session_state.nickname = nickname
    character=st.text_area("性格",placeholder="请输入性格",value=st.session_state.character)
    if character:
        session_state.character = character

#消息输入框
prompt = st.chat_input("请输入您要咨询的问题")
if prompt:#字符串会自动转化为布尔值，非空为True
    st.chat_message("user").write(prompt)
    print("----------------> 调用AI大模型，提示词：", prompt)
    #保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

 # 调用AI大模型（获取流式生成器）
    response = agent_loop(prompt)

    # 创建空容器（像一个可擦写的黑板，可以在一个位置反复更新）
    response_message = st.empty()
    full_response = ""
    # 流式逐块读取并实时更新 → 打字机效果
    for chunk in response:#遍历每一个数据包
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            # 每次追加新内容后，刷新整个容器的显示
            response_message.chat_message("assistant").write(full_response)

    print("<---------------- AI回复：", full_response)
    # 保存完整的AI回复（注意是 full_response 字符串，不是生成器）
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存会话信息
    save_session()

