# coding=utf-8

from typing import List, Type

__all__ = ['Annotation', 'AnnotationMetadata', 'AnnotationUtils']


class Annotation:

    def __init__(self, **kwargs):
        self.attributes = {}
        self.attributes.update(kwargs)

    def __contains__(self, key):
        return key in self.attributes

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __getitem__(self, key):
        return self.attributes.get(key)


class AnnotationMetadata:
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


ANNOTATION_METADATA = '__annotation_metadata'


class AnnotationUtils:

    @staticmethod
    def get_annotation_metadata(source) -> AnnotationMetadata:
        if hasattr(source, ANNOTATION_METADATA):
            metadata = getattr(source, ANNOTATION_METADATA)
            # annotations on class cannot be inherited
            if not isinstance(metadata.source, type) or metadata.source == source:
                return metadata

    @staticmethod
    def get_annotation(source, annotation_type: Type[Annotation]) -> Annotation:
        annotation_metadata = AnnotationUtils.get_annotation_metadata(source)
        if annotation_metadata is not None:
            return annotation_metadata.get_annotation(annotation_type)

    @staticmethod
    def get_annotations(source) -> List[Annotation]:
        annotation_metadata = AnnotationUtils.get_annotation_metadata(source)
        if annotation_metadata is not None:
            return annotation_metadata.annotations
        return []

    @staticmethod
    def add_annotation(source, annotation: Annotation):
        annotation_metadata = AnnotationUtils.get_annotation_metadata(source)
        if annotation_metadata is None:
            annotation_metadata = AnnotationMetadata(source)
            setattr(source, ANNOTATION_METADATA, annotation_metadata)
        annotation_metadata.add_annotation(annotation)
