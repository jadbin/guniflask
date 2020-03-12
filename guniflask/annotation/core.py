# coding=utf-8

from typing import List, Type

__all__ = ['Annotation', 'AnnotationMetadata']


class Annotation:

    def __init__(self, **kwargs):
        self.attributes = {}
        self.attributes.update(kwargs)

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __getitem__(self, key):
        return self.attributes.get(key)


class AnnotationMetadata:
    key = '__annotation_metadata'

    def __init__(self, source):
        if not hasattr(source, '__name__'):
            raise ValueError('Cannot annotate to the object without "__name__" attribute')
        self._source = source
        self._annotations = {}

    @property
    def source(self):
        return self._source

    def add_annotation(self, annotation: Annotation):
        self._annotations[type(annotation)] = annotation

    def get_annotation(self, annotation_type: Type[Annotation]) -> Annotation:
        return self._annotations.get(annotation_type)

    @property
    def annotations(self) -> List[Annotation]:
        return list(self._annotations.values())

    def is_annotated(self, annotation_type: Type[Annotation]) -> bool:
        for a in self._annotations.values():
            if isinstance(a, annotation_type):
                return True
        return False
