# 1. 拿到键盘的操作权限
fd = sys.stdin.fileno()  # fd = 0

# 2. 记录键盘当前的所有设置
old_settings = termios.tcgetattr(fd)  # 保存原始设置

# 3. 修改键盘设置（变成原始模式）
tty.setraw(fd)  # 改成：不需要按回车、不显示按键

# 4. 读取按键
key = sys.stdin.read(1)

# 5. 恢复键盘到原始设置
termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
--------------------------------------------------------------------------
old = termios.tcgetattr(fd) # 1. 先记住原来的设置
try:
    tty.setraw(fd)          # 2. 改成我们需要的“原始模式”
    # ... 你的核心代码 ...
finally:
    # 3. 无论上面的代码是否出错，都一定会执行这里，把终端恢复原样！
    termios.tcsetattr(fd, termios.TCSADRAIN, old)
----------------------------------------------------------------------

# 用户按了 'w'
dr, dw, de = select.select([sys.stdin], [], [], 0.1)

# 结果：
dr = [sys.stdin]  # ← 有输入！列表不为空
dw = []           # ← 没有可写的
de = []           # ← 没有错误

# 0.1秒内没有任何按键
dr, dw, de = select.select([sys.stdin], [], [], 0.1)

# 结果：
dr = []  # ← 没有输入！列表为空
dw = []  # ← 没有可写的
de = []  # ← 没有错误

调用 select.select([sys.stdin], [], [], 0.1)
            │
            ▼
    ┌───────────────────┐
    │  等待 0.1 秒       │
    │  同时盯着键盘      │
    └───────────────────┘
            │
            ├─── 有按键 ───→ dr = [sys.stdin]
            │
            └─── 无按键 ───→ dr = []
            │
            ▼
    if dr:（判断是否有输入）
            │
            ├─── True ───→ sys.stdin.read(1) 读取按键
            │
            └─── False ───→ return None
----------------------------------------------------------
