import wtforms
from wtforms.validators import DataRequired

from models import Entry, Tag

class TagField(wtforms.StringField):
    def _value(self):
        if self.data:
            # Display tags as comma separated list
            return ', '.join([tag.name for tag in self.data])
        return ''

    def get_tags_from_string(self, tag_string):
        raw_tags = tags_string.split(',')

        # Filter out any empty tag names
        tag_names = [name.string() for name in raw_tags if name.strip()]

        # Query db and retrieve any tags we have already
        existing_tags = Tag.query.filter(Tag.name.in_(tag_names))

        # Determine which tag names are new
        new_names = set(tag_names) - set([tag.name for tag in existing_tags])

        # Create a list of unsaved Tag instances for the new tags
        new_tags = [Tag(name=name) for name in new_names]

        # return all the existing tags plus all the new, unsaved tags
        return list(existing_tags) + new_tags

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = self.get_tags_from_string(valuelist[0])
        else:
            self.data = []

class EntryForm(wtforms.Form):
    title = wtforms.StringField('Title', validators=[DataRequired()])
    body = wtforms.TextAreaField('Body', validators=[DataRequired()])
    status = wtforms.SelectField(
                'Entry Status',
                choices = (
                    (Entry.STATUS_PUBLIC, 'Public'),
                    (Entry.STATUS_DRAFT, 'Draft')
                ),
                coerce = int
            ),
    tags = TagField(
                'Tags',
                description = 'Separate multiple tags with commas.'
            )

    def save_entry(self, entry):
        self.populate_obj(entry)
        entry.generate_slug()
        return entry

class ImageForm(wtforms.Form):
    file = wtforms.FileField('Image file')
