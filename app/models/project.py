from app import db, ma
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


# Define Project model
class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(96), server_default='')
    site_url = db.Column(db.String(96), server_default='')
    github_url = db.Column(db.String(96), server_default='')
    alt = db.Column(db.String(32), server_default='project')
    title = db.Column(db.String(48), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=True)
    read_me = db.Column(db.LargeBinary(), server_default='')
    topic_main = db.Column(db.String(32), server_default='')
    topics = db.relationship(
        'Topic',
        cascade='all,delete',
        secondary='project_topics',
        backref=db.backref('project', lazy='dynamic')
    )


# Define Topic model
class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(48), unique=True)
    profeciency = db.Column(db.Integer(), nullable=False)


# Define ProjectTopics model
class ProjectTopics(db.Model):
    __tablename__ = 'project_topics'
    id = db.Column(db.Integer(), primary_key=True)
    project_id = db.Column(
        db.Integer(),
        db.ForeignKey('project.id', ondelete='CASCADE')
    )
    topic_id = db.Column(
        db.Integer(),
        db.ForeignKey('topic.id', ondelete='CASCADE')
    )


# Define ProjectSchema
class ProjectSchema(ma.ModelSchema):
    class Meta:
        model = Project
        ordered = True

    topics = fields.Nested('TopicSchema', many=True, load=True)


# Define TopicSchema
class TopicSchema(ma.ModelSchema):
    class Meta:
        model = Topic


# Define ProjectTopicsSchema
class ProjectTopicsSchema(ma.ModelSchema):
    class Meta:
        model = ProjectTopics
