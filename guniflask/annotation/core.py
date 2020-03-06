# coding=utf-8

from typing import List

__all__ = ['Annotation', 'AnnotationMetadata']


class Annotation:

    def __init__(self, **kwargs):
        self._type = self.__class__
        self.attributes = {}
        self.attributes.update(kwargs)

    @property
    def annotation_type(self) -> type:
        return self._type

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __getitem__(self, key):
        return self.attributes.get(key)


class AnnotationMetadata:
    key = '__annotation_metadata'

    def __init__(self, source):
        self._source = source
        self._annotations = {}

    @property
    def source(self):
        return self._source

    def add_annotation(self, annotation: Annotation):
        self._annotations[annotation.annotation_type] = annotation

    def get_annotation(self, annotation_type: type) -> Annotation:
        return self._annotations.get(annotation_type)

    @property
    def annotations(self) -> List[Annotation]:
        return list(self._annotations.values())

    def is_annotated(self, annotation_type: type) -> bool:
        for a in self._annotations.values():
            if isinstance(a, annotation_type):
                return True
        return False
