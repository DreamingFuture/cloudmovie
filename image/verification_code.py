from PIL import Image, ImageFilter, ImageDraw, ImageFont
from random import randint, choices, choice
from io import BytesIO


class Code:
    def __init__(self, length=5):
        # 创建字符库
        chars = ['2', '3', '4', '5', '6', '7', '8', '9']
        up_alphabet = [chr(num) for num in range(65, 91)]
        down_alphabet = [chr(num) for num in range(97, 123)]
        chars.extend(up_alphabet)
        chars.extend(down_alphabet)
        chars.remove('O')
        chars.remove('o')
        chars.remove('l')
        chars.remove('L')
        chars.remove('i')
        chars.remove('I')
        self.__chars = chars
        # 字符长度定义
        self.__length = length
        # 图片尺寸
        self.__width = length * 60
        self.__height = 120
        # 背景色
        self.__back_color = self.__rand_back_color()
        # 创建Image对象
        self.__image = Image.new('RGB', (self.__width, self.__height), self.__back_color)
        # 创建ImageDraw对象
        self.__draw = ImageDraw.Draw(self.__image)

    @staticmethod
    def __rand_back_color():
        # 背景颜色
        r = randint(155, 256)
        g = randint(155, 256)
        b = randint(155, 256)
        return r, g, b

    @staticmethod
    def __rand_line_color():
        # 干扰线颜色
        r = randint(0, 256)
        g = randint(0, 256)
        b = randint(0, 256)
        return r, g, b

    @staticmethod
    def __rand_char_color():
        # 验证码颜色
        r = randint(0, 155)
        g = randint(0, 155)
        b = randint(0, 155)
        return r, g, b

    @staticmethod
    def __rand_font():
        # 随机字体
        path = 'C:\Windows\Fonts\Arial.ttf'
        size = randint(45, 50)
        font = ImageFont.truetype(path, size)
        return font

    def __rand_point_color(self):
        # 噪点颜色
        back_color = self.__back_color
        r = randint(back_color[0] - 40, back_color[0] + 40)
        g = randint(back_color[1] - 40, back_color[1] + 40)
        b = randint(back_color[2] - 40, back_color[2] + 40)
        return r, g, b

    def __rand_point(self):
        # 画若干干扰点
        for n in range(randint(80, 120)):
            x = randint(0, self.__width)
            y = randint(0, self.__height)
            coordinate = (x, y, x + 4, y + 4)
            self.__draw.arc(coordinate, 0, 90, fill=(0, 0, 0))

    def __rand_string(self):
        # 获取随机验证码并在图像中画出，返回验证码
        chars = choices(self.__chars, k=self.__length)
        string = ''.join(chars)
        for n in range(len(string)):
            self.__draw.text((60*n + 10, randint(20, 70)), string[n], font=self.__rand_font(), fill=self.__rand_char_color())
        return string

    def __rand_line(self):
        # 随机画3-6条像素宽度2-4的干扰线
        for n in range(randint(3, 7)):
            begin = (randint(0, self.__width), randint(0, self.__height))
            end = (randint(0, self.__width), randint(0, self.__height))
            color = self.__rand_line_color()
            for i in range(randint(2, 5)):
                self.__draw.line([(begin[0] + i, begin[1] + i), (end[0] + i, end[1]+i)], fill=color)

    def make_code(self):
        # 噪点填充
        for x in range(self.__width):
            for y in range(self.__height):
                self.__draw.point((x, y), fill=self.__rand_point_color())
        # 干扰点填充
        self.__rand_point()
        # 验证码填充
        string = self.__rand_string()
        # 干扰线填充
        self.__rand_line()
        # 模糊处理
        self.__image.filter(ImageFilter.DETAIL)

        buf = BytesIO()
        self.__image.save(buf, 'png')
        # 返回验证码及图片
        return string, buf


