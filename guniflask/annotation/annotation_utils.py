# coding=utf-8

from guniflask.annotation.core import Annotation, AnnotationMetadata


def get_annotation(annotated_element, annotation_type: Annotation):
    if hasattr(annotated_element, AnnotationMetadata.key):
        annotation_metadata = getattr(annotated_element, AnnotationMetadata.key)
        return annotation_metadata.get_annotation(annotation_type)
    return None


def get_annotations(annotated_element):
    if hasattr(annotated_element, AnnotationMetadata.key):
        annotation_metadata = getattr(annotated_element, AnnotationMetadata.key)
        return annotation_metadata.annotations
    return []


def add_annotation(annotated_element, annotation: Annotation):
    if not hasattr(annotated_element, AnnotationMetadata.key):
        annotation_meta = AnnotationMetadata(annotated_element)
        setattr(annotation, AnnotationMetadata.key, annotation_meta)
    else:
        annotation_meta = getattr(annotated_element, AnnotationMetadata.key)
    annotation_meta.add_annotation(annotation)
