# coding=utf-8

from typing import List, Type

from guniflask.annotation.core import Annotation, AnnotationMetadata

__all__ = ['AnnotationUtils']

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
