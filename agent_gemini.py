from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from tools import search_flights, search_hotels, calculate_budget
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# 1. Đọc System Prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM và Tools
tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent Node
def agent_node(state: AgentState):
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"[LOG] Gọi tool: {tc['name']}({tc['args']})")
    else:
        print("[LOG] Trả lời trực tiếp")
        
    return {"messages": [response]}
# 4. Agent Node
# def agent_node(state: AgentState):
#     messages = state["messages"]
    
#     with open("system_prompt.txt", "r", encoding="utf-8") as f:
#         fresh_system_prompt = f.read()
        
#     filtered_messages = [m for m in messages if not isinstance(m, SystemMessage)]
    
#     messages_for_llm = [SystemMessage(content=fresh_system_prompt)] + filtered_messages
        
#     response = llm_with_tools.invoke(messages_for_llm)
    
#     # === LOGGING ===
#     if response.tool_calls:
#         for tc in response.tool_calls:
#             print(f"[LOG] Gọi tool: {tc['name']}({tc['args']})")
#     else:
#         print("[LOG] Trả lời trực tiếp")
        
#     return {"messages": [response]}

# 5. Xây dựng Graph
builder = StateGraph(AgentState)

# Thêm Nodes
builder.add_node("agent", agent_node)
tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

# ==========================================
# KHAI BÁO EDGES (Luồng thực thi của Agent)
# ==========================================
# Điểm bắt đầu luôn trỏ vào node agent
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
# ==========================================

# Thêm MemorySaver để lưu lịch sử hội thoại
# memory = MemorySaver()

# Compile graph KÈM THEO checkpointer
# graph = builder.compile(checkpointer=memory)

graph = builder.compile()


# 6. Chat loop
if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy - Trợ lý Du lịch Thông minh")
    print(" Gõ 'quit' hoặc 'exit' để thoát")
    print("=" * 60)
    
    # Cấu hình thread_id. Những tin nhắn có cùng thread_id sẽ được Agent nhớ
    config = {"configurable": {"thread_id": "thread_1"}}
    
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
            
        print("\nTravelBuddy đang suy nghĩ...")
        
        # Truyền thêm config vào hàm invoke
        result = graph.invoke(
            {"messages": [("human", user_input)]}, 
            config=config # <--- QUAN TRỌNG: Phải có config chứa thread_id
        )
        
        # Lấy tin nhắn cuối cùng (câu trả lời của bot)
        final = result["messages"][-1]
        print(f"\nTravelBuddy: {final.content}")