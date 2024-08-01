# coding:utf-8
import re
import flet as ft
from PyPDF2 import PdfReader as reader, PdfWriter as writer
from bisect import bisect_right

FILE_PATH = None
FILE_NAME = None
wasted_string = "…· ……"


def main(mypage: ft.Page):
    mypage.title = "添加书签"
    mypage.padding = 20
    mypage.window_left = 10
    mypage.window_top = 10
    mypage.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    mypage.snack_bar = ft.SnackBar(
        bgcolor=ft.colors.GREEN,
        content=ft.Text("成功添加书签"),
        action="ok"
    )

    def pick_files_result(e: ft.FilePickerResultEvent):
        global FILE_PATH
        global FILE_NAME
        selected_files.value = (
            ", ".join(map(lambda f: f.name, e.files)
                      ) if e.files else "Cancelled!"
        )
        FILE_PATH = e.files[0].path
        FILE_NAME = e.files[0].name
        output_name.value = e.files[0].name.split(".")[0] + "[带书签].pdf"
        output_name.update()
        print(FILE_PATH)
        selected_files.update()

    def clean_line(line: str):
        for i in wasted_string:
            line = line.replace(i, "")

    def add_mark(e):
        global FILE_PATH
        global FILE_NAME
        # 输出文件位置
        output_path = FILE_PATH.rstrip(FILE_NAME) + output_name.value
        print(output_path)
        print(shift.value)
        shift_value = int(shift.value)  # 实际页数与标注页数的差值

        pages = []
        chapters = []
        parents = []
        int_chapters = []

        for line in mulu.value.splitlines():
            if line.startswith(" "):
                clean_line(line)
                pages.append(line)
            else:
                clean_line(line)
                chapters.append(line)
        print(chapters)
        print(pages)

        pdf_in = reader(FILE_PATH)   # 读取PDF文件
        pdf_out = writer()          # 创建一个可写的PDF对象

        page_sum = len(pdf_in.pages)

        for i in range(page_sum):
            pdf_out.add_page(pdf_in.pages[i])

        for chapter in chapters:
            try:
                pagenum = int(re.findall(r"\d+", chapter)[-1])
                int_chapters.append(pagenum)
                parent = pdf_out.add_outline_item(
                    chapter, pagenum + shift_value - 1)
                parents.append(parent)
            except Exception as e:
                print(e)
                pass

        def find_parent(page, chapter):
            return (bisect_right(chapter, page))

        for page in pages:
            # 寻找多个(1)(2)中最后一个数字
            pagenum = int(re.findall(r"\d+", page)[-1])
            parent_index = find_parent(pagenum, int_chapters)
            try:
                pdf_out.add_outline_item(
                    page, pagenum + shift_value - 1, parent=parents[parent_index - 1])
            except Exception as e:
                print(e)
                pass

        try:
            pdf_out.write(open(output_path, 'wb'))
            mypage.snack_bar.open = True
            mypage.update()

        except Exception as e:
            print(e)
            pass

    mulu = ft.TextField(
        label="粘贴目录",
        multiline=True,
        min_lines=1,
        max_lines=300,
    )

    shift = ft.TextField(
        value="0",
        label="页码偏移",
    )

    output_name = ft.TextField(
        label="输出文件名",
    )

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    selected_files = ft.Text()

    mypage.overlay.append(pick_files_dialog)
    mypage.add(
        ft.Row(
            [
                ft.Container(
                    bgcolor=ft.colors.BLUE_GREY_100,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.START,
                        height=800,
                        width=250,
                        controls=[
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "选择PDF文件",
                                    icon=ft.icons.UPLOAD_FILE,
                                    on_click=lambda _: pick_files_dialog.pick_files(
                                        allow_multiple=True
                                    )
                                ),
                            ),
                            ft.Container(
                                content=selected_files
                            ),
                            ft.Container(
                                content=shift,
                            ),
                            ft.Container(
                                content=output_name,
                            ),
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "添加目录",
                                    on_click=add_mark
                                )
                            ),

                        ],
                    ),
                ),
                ft.Container(
                    height=800,
                    width=800,
                    content=mulu
                ),
            ],
        ),
    )


if __name__ == "__main__":
    ft.app(target=main)
