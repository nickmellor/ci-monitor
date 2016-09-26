# OS-agnostic message-handling
import os
import sys
import traceback

class Message:

    def __init__(self, first_line=None, indent=0):
        self.message = []
        self.indent = indent
        if first_line:
            self.message.append((first_line, 0))

    def add(self, line):
        self.message.append((line, self.indent))

    def indent(self, spaces=4):
        self.indent += spaces

    def outdent(self, spaces=4):
        self.indent -= spaces

    def add_lines(self, lines):
        for line in lines:
            self.add(line)

    def add_text(self, text):
        for line in text.splitlines():
            self.add(line)

    def add_text_summary(self, text, max_size=10):
        # summary of a text with ellipsis for middle of longer texts
        message_lines = text.splitlines()
        # if it's a short text show all of it
        if len(message_lines) <= max_size:
            self.add_lines(message_lines)
        else:
            # print head and tail of the text with ellipsis for the middle section
            self.add_lines(message_lines[:max_size // 2 - 1] + ['   [...]'] + message_lines[-max_size // 2:])

    def add_code_summary(self, text, max_size=10):
        # summary of code with ellipsis for middle of longer fragments
        message_lines = ['{lineno}: {line}'.format(lineno=lineno_zero + 1, line=line)
                           for lineno_zero, line in enumerate(text.splitlines())]
        # if it's a short text show all of it
        if len(message_lines) <= max_size:
            self.add_lines(message_lines)
        else:
            # print head and tail of the text with ellipsis for the middle section
            self.add_lines(message_lines[:max_size // 2 - 1] + ['   [...]'] + message_lines[-max_size // 2:])

    def out(self):
        # if last line of text was not blank add a newline to avoid same-line collisions
        if self.message[-1][0].strip():
            self.add('')
        return os.linesep.join(' ' * indent + line for line, indent in self.message)


def exception_summary():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    return(traceback.format_tb(exc_tb))




if __name__ == '__main__':
    indent = 4
    t = Message(indent=indent)
    t.add_code_summary("""Line 1
Line2
Line3
Line4
Line5
Line6
Line7
Line8
Line9
Line10
Line11""")
    print(t.out())

    try:
        1/0
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        exc_filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        for frame in traceback.format_tb(exc_tb):
            print(frame)