from tortoise import Model, fields

from app.state import State


class User(Model):
    id = fields.BigIntField(pk=True)
    state = fields.TextField(default=State.default)
    state_data = fields.JSONField(default={})

    courses: fields.ReverseRelation["Course"]
    participations: fields.ManyToManyRelation["Course"] = fields.ManyToManyField(
        "models.Course", related_name="participants", through="user_course"
    )


class Course(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    author = fields.ForeignKeyField("models.User", related_name="courses")

    participants: fields.ManyToManyRelation[User]
    lessons: fields.ReverseRelation["Lesson"]


class Lesson(Model):
    id = fields.IntField(pk=True)
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    course = fields.ForeignKeyField("models.Course", related_name="lessons")
