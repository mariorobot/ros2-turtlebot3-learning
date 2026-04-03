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
