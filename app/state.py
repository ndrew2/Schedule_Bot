from enum import Enum


class State(str, Enum):
    default = 'default'
    add_course_2 = 'add_course_2'
    add_lesson_2 = 'add_lesson_2'
    add_lesson_3 = 'add_lesson_3'
    add_lesson_4 = 'add_lesson_4'
    add_lesson_5 = 'add_lesson_5'
    delete_course_2 = 'delete_course_2'
    get_link_2 = 'get_link_2'
