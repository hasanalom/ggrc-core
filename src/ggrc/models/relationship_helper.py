# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: miha@reciprocitylabs.com
# Maintained By: miha@reciprocitylabs.com

from sqlalchemy import and_
from sqlalchemy import sql

from ggrc import db
from ggrc.extensions import get_extension_modules
from ggrc import models
from ggrc.models import Audit
from ggrc.models import AuditObject
from ggrc.models import Section
from ggrc.models import Request
from ggrc.models import Response
from ggrc.models.relationship import Relationship
from ggrc.models import all_models


class RelationshipHelper(object):

  @classmethod
  def section_directive(cls, object_type, related_type, related_ids):
    directives = {"Policy", "Regulation", "Standard"}
    if not related_ids:
      return None

    if object_type == "Section" and related_type in directives:
      return db.session.query(Section.id).filter(
          Section.directive_id.in_(related_ids))
    elif related_type == "Section" and object_type in directives:
      return db.session.query(Section.directive_id).filter(
          Section.id.in_(related_ids))

    return None

  @classmethod
  def program_audit(cls, object_type, related_type, related_ids):
    if {object_type, related_type} != {"Program", "Audit"} or not related_ids:
      return None

    if object_type == "Program":
      return db.session.query(Audit.program_id).filter(
          Audit.id.in_(related_ids))
    else:
      return db.session.query(Audit.id).filter(
          Audit.program_id.in_(related_ids))

  @classmethod
  def person_withcontact(cls, object_type, related_type, related_ids):
    object_model = getattr(models, object_type, None)
    related_model = getattr(models, related_type, None)
    if None in [object_model, related_model]:
      return None
    if object_model == models.Person:
      if issubclass(related_model, models.mixins.WithContact):
        return db.session.query(related_model.contact_id).filter(
            related_model.id.in_(related_ids)).union(
            db.session.query(related_model.secondary_contact_id).filter(
                related_model.id.in_(related_ids)))
      else:
        return None
    elif related_model == models.Person:
      if issubclass(object_model, models.mixins.WithContact):
        return db.session.query(object_model.id).filter(
            object_model.contact_id.in_(related_ids) |
            object_model.secondary_contact_id.in_(related_ids))
    else:
      return None

  @classmethod
  def person_ownable(cls, object_type, related_type, related_ids):
    if object_type == "Person":
      return db.session.query(models.ObjectOwner.person_id).filter(
          (models.ObjectOwner.ownable_type == related_type) &
          (models.ObjectOwner.ownable_id.in_(related_ids)))
    elif related_type == "Person":
      return db.session.query(models.ObjectOwner.ownable_id).filter(
          (models.ObjectOwner.ownable_type == object_type) &
          (models.ObjectOwner.person_id.in_(related_ids)))
    else:
      return None

  @classmethod
  def person_object(cls, object_type, related_type, related_ids):
    if "Person" not in [object_type, related_type]:
      return None
    if object_type == "Person":
      return db.session.query(models.ObjectPerson.person_id).filter(
          (models.ObjectPerson.personable_type == related_type) &
          (models.ObjectPerson.personable_id.in_(related_ids))
      )
    else:
      return db.session.query(models.ObjectPerson.personable_id).filter(
          (models.ObjectPerson.personable_type == object_type) &
          (models.ObjectPerson.person_id.in_(related_ids))
      )

  @classmethod
  def audit_request(cls, object_type, related_type, related_ids):
    if {object_type, related_type} != {"Audit", "Request"} or not related_ids:
      return None

    if object_type == "Audit":
      return db.session.query(Request.audit_id).filter(
          Request.id.in_(related_ids))
    else:
      return db.session.query(Request.id).filter(
          Request.audit_id.in_(related_ids))

  @classmethod
  def request_assignee(cls, object_type, related_type, related_ids):
    if {object_type, related_type} != {"Person", "Request"} or not related_ids:
      return None

    if object_type == "Person":
      return db.session.query(Request.assignee_id).filter(
          Request.id.in_(related_ids))
    else:
      return db.session.query(Request.id).filter(
          Request.assignee_id.in_(related_ids))

  @classmethod
  def request_audit_object(cls, object_type, related_type, related_ids):
    if object_type == "Request":
      return db.session.query(Request.id).join(AuditObject).filter(
          (AuditObject.auditable_type == related_type) &
          AuditObject.auditable_id.in_(related_ids))
    elif related_type == "Request":
      return db.session.query(AuditObject.auditable_id).join(Request).filter(
          (AuditObject.auditable_type == related_type) &
          Request.id.in_(related_ids))
    else:
      return None

  @classmethod
  def request_response(cls, object_type, related_type, related_ids):
    if {object_type, related_type} != {"Request", "Response"} or not related_ids:
      return None
    if object_type == "Request":
      return db.session.query(Response.request_id).filter(
          Response.id.in_(related_ids))
    else:
      return db.session.query(Response.id).filter(
          Response.request_id.in_(related_ids))

  @classmethod
  def program_risk_assessment(cls, object_type, related_type, related_ids):
    if {object_type, related_type} != {"Program", "RiskAssessment"} or not related_ids:
      return None
    if object_type == "Program":
      return db.session.query(all_models.RiskAssessment.program_id).filter(
          all_models.RiskAssessment.id.in_(related_ids))
    else:
      return db.session.query(all_models.RiskAssessment.id).filter(
          all_models.RiskAssessment.program_id.in_(related_ids))

  @classmethod
  def task_group_object(cls, object_type, related_type, related_ids):
    if not related_ids:
      return None
    if object_type == "TaskGroup":
      return db.session.query(all_models.TaskGroupObject.task_group_id).filter(
          (all_models.TaskGroupObject.object_type == related_type) &
          all_models.TaskGroupObject.object_id.in_(related_ids))
    elif related_type == "TaskGroup":
      return db.session.query(all_models.TaskGroupObject.object_id).filter(
          (all_models.TaskGroupObject.object_type == related_type) &
          all_models.TaskGroupObject.task_group_id.in_(related_ids))
    else:
      return None

  @classmethod
  def get_special_mappings(cls, object_type, related_type, related_ids):
    return [
        cls.audit_request(object_type, related_type, related_ids),
        cls.person_object(object_type, related_type, related_ids),
        cls.person_ownable(object_type, related_type, related_ids),
        cls.person_withcontact(object_type, related_type, related_ids),
        cls.program_audit(object_type, related_type, related_ids),
        cls.program_risk_assessment(object_type, related_type, related_ids),
        cls.request_assignee(object_type, related_type, related_ids),
        cls.request_audit_object(object_type, related_type, related_ids),
        cls.request_response(object_type, related_type, related_ids),
        cls.section_directive(object_type, related_type, related_ids),
        cls.task_group_object(object_type, related_type, related_ids),
    ]

  @classmethod
  def get_extension_mappings(cls, object_type, related_type, related_ids):
    queries = []
    for extension in get_extension_modules():
      get_ids = getattr(extension, "contributed_get_ids_related_to", None)
      if callable(get_ids):
        queries.append(get_ids(object_type, related_type, related_ids))
    return queries

  @classmethod
  def _array_union(cls, queries):
    """ Union of all valid queries in array """
    clean_queries = [q for q in queries if q is not None]
    if len(clean_queries) == 0:
      return db.session.query(Relationship.source_id).filter(sql.false())

    query = clean_queries.pop()
    for q in clean_queries:
      query = query.union(q)
    return query

  @classmethod
  def get_ids_related_to(cls, object_type, related_type, related_ids=[]):
    """ get ids of objects

    Get a list of all ids for object with object_type, that are related to any
    of the objects with type related_type and id in related_ids
    """

    if isinstance(related_ids, (int, long)):
      related_ids = [related_ids]

    if not related_ids:
      return db.session.query(Relationship.source_id).filter(sql.false())

    destination_ids = db.session.query(Relationship.destination_id).filter(
        and_(
            Relationship.destination_type == object_type,
            Relationship.source_type == related_type,
            Relationship.source_id.in_(related_ids),
        )
    )
    source_ids = db.session.query(Relationship.source_id).filter(
        and_(
            Relationship.source_type == object_type,
            Relationship.destination_type == related_type,
            Relationship.destination_id.in_(related_ids),
        )
    )

    queries = [destination_ids, source_ids]
    queries.extend(cls.get_extension_mappings(
        object_type, related_type, related_ids))
    queries.extend(cls.get_special_mappings(
        object_type, related_type, related_ids))

    return cls._array_union(queries)
