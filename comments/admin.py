import uuid
from django.contrib import admin
from django import forms
from comments.models import Comment
from treebeard.admin import TreeAdmin
from treebeard.forms import MoveNodeForm
from django.utils.translation import ugettext_lazy as _


class CommentForm(MoveNodeForm):
    """
    A form class for creating new comments.
    """
    _ref_node_id = forms.ChoiceField(label=_("Relative to"))

    class Meta:
        model = Comment
        fields = ('author', 'film', 'tv', 'text', '_position', '_ref_node_id')

    def _clean_cleaned_data(self):
        """ delete auxilary fields not belonging to node model """
        reference_node_id = uuid.uuid4()

        if '_ref_node_id' in self.cleaned_data:
            if self.cleaned_data['_ref_node_id'] == '0':  # is root
                reference_node_id = uuid.uuid4()
            else:
                reference_node_id = self.cleaned_data['_ref_node_id']
            del self.cleaned_data['_ref_node_id']

        position_type = self.cleaned_data['_position']
        del self.cleaned_data['_position']

        return position_type, reference_node_id

    def save(self, commit=True):
        """
        Overriding .save() for correct changing the comment tree by admin user.
        :param commit: specifying the creating new instance of comment.
        :return: new Comment instance.
        """
        position_type, reference_node_id = self._clean_cleaned_data()
        if position_type == 'sorted-child':  # implementing logic for creating child comment
            try:
                reference_node = self._meta.model.objects.get(pk=reference_node_id)
                self.instance = reference_node.add_child(**self.cleaned_data)
            except self._meta.model.DoesNotExist:   # it is a root
                self.instance = self._meta.model.add_root(**self.cleaned_data)
        else:  # creating sibling
            try:
                reference_node = self._meta.model.objects.get(pk=reference_node_id)
                self.instance = reference_node.add_sibling(**self.cleaned_data)
            except self._meta.model.DoesNotExist:   # it is a root
                self.instance = self._meta.model.add_root(**self.cleaned_data)
        # Reload the instance
        super(MoveNodeForm, self).save(commit=commit)  # noqa
        return self.instance


@admin.register(Comment)
class CommentAdmin(TreeAdmin):
    form = CommentForm
