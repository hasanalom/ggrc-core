# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: miha@reciprocitylabs.com
# Maintained By: miha@reciprocitylabs.com

import random
import copy
from tests.ggrc import TestCase

import os
from ggrc import db
from ggrc_workflows.models import Workflow, TaskGroup, CycleTaskGroupObjectTask, Cycle
from tests.ggrc_workflows.generator import WorkflowsGenerator
from tests.ggrc.api_helper import Api
from tests.ggrc.generator import GgrcGenerator


if os.environ.get('TRAVIS', False):
  random.seed(1)  # so we can reproduce the tests if needed


class TestWorkflowActivation(TestCase):

  def setUp(self):
    self.api = Api()
    self.generator = WorkflowsGenerator()
    self.ggrc_generator = GgrcGenerator()

    self.random_objects = self.generator.generate_random_objects()
    self.create_test_cases()

  def tearDown(self):
    pass

  def test_create_workflows(self):
    wf_dict = copy.deepcopy(self.one_time_workflow_1)
    _, wf = self.generator.generate_workflow(wf_dict)
    self.assertIsInstance(wf, Workflow)

    task_groups = db.session.query(TaskGroup)\
        .filter(TaskGroup.workflow_id == wf.id).all()

    self.assertEqual(len(task_groups),
                     len(self.one_time_workflow_1["task_groups"]))

  def test_weekly_workflows(self):
    wf_dict = copy.deepcopy(self.weekly_wf_1)
    _, wf = self.generator.generate_workflow(wf_dict)
    self.assertIsInstance(wf, Workflow)

    task_groups = db.session.query(TaskGroup)\
        .filter(TaskGroup.workflow_id == wf.id).all()

    self.assertEqual(len(task_groups),
                     len(self.weekly_wf_1["task_groups"]))

  def test_activate_one_time_wf(self):
    wf_dict = copy.deepcopy(self.one_time_workflow_1)
    _, wf = self.generator.generate_workflow(wf_dict)
    self.assertIsInstance(wf, Workflow)
    task_groups = db.session.query(TaskGroup)\
        .filter(TaskGroup.workflow_id == wf.id).all()
    self.assertEqual(len(task_groups),
                     len(self.one_time_workflow_1["task_groups"]))

    response, wf = self.generator.activate_workflow(wf)

  def test_one_time_workflow_edits(self):
    wf_dict = copy.deepcopy(self.one_time_workflow_1)
    _, wf = self.generator.generate_workflow(wf_dict)

    wf_dict = {"title": "modified one time wf"}
    self.generator.modify_workflow(wf, data=wf_dict)

    modified_wf = db.session.query(Workflow).filter(Workflow.id == wf.id).one()
    self.assertEqual(wf_dict["title"], modified_wf.title)

  def test_one_time_wf_activate(self):
    wf_dict = copy.deepcopy(self.one_time_workflow_1)
    _, wf = self.generator.generate_workflow(wf_dict)
    self.generator.generate_cycle(wf)
    self.generator.activate_workflow(wf)

    tasks = [len(tg.get("task_group_tasks", [])) * max(1, len(tg.get("task_group_objects", [])))
             for tg in self.one_time_workflow_1["task_groups"]]

    cycle_tasks = db.session.query(CycleTaskGroupObjectTask).join(
      Cycle).join(Workflow).filter(Workflow.id == wf.id).all()
    active_wf = db.session.query(Workflow).filter(Workflow.id == wf.id).one()

    self.assertEqual(sum(tasks), len(cycle_tasks))
    self.assertEqual(active_wf.status, "Active")

  def test_delete_calls(self):
    _, workflow = self.generator.generate_workflow()
    self.generator.generate_task_group(workflow)
    _, task_group = self.generator.generate_task_group(workflow)
    task_groups = db.session.query(TaskGroup).filter(TaskGroup.workflow_id == workflow.id).all()
    self.assertEqual(len(task_groups), 2)

    response = self.generator.api.delete(task_group, task_group.id)
    self.assert200(response)

    task_groups = db.session.query(TaskGroup).filter(TaskGroup.workflow_id == workflow.id).all()
    self.assertEqual(len(task_groups), 1)


  def create_test_cases(self):
    self.weekly_wf_1 = {
      "title": "weekly thingy",
      "description": "start this many a time",
      "frequency": "weekly",
      "task_groups": [{
          "title": "tg_2",
          "task_group_tasks": [{
              "description": self.generator.random_str(100),
              "relative_end_day": 1,
              "relative_end_month": None,
              "relative_start_day": 5,
              "relative_start_month": None,
            }, {
              "title": "monday task",
              "relative_end_day": 1,
              "relative_end_month": None,
              "relative_start_day": 1,
              "relative_start_month": None,
            }, {
              "title": "weekend task",
              "relative_end_day": 4,
              "relative_end_month": None,
              "relative_start_day": 1,
              "relative_start_month": None,
            },
          ],
          "task_group_objects": self.random_objects
        },
      ]
    }

    self.one_time_workflow_1 = {
      "title": "one time wf test",
      "description": "some test workflow",
      "task_groups": [{
          "title": "tg_1",
          "task_group_tasks": [{}, {}, {}]
        }, {
          "title": "tg_2",
          "task_group_tasks": [{
              "description": self.generator.random_str(100)
            }, {}
          ],
          "task_group_objects": self.random_objects[:2]
        }, {
          "title": "tg_3",
          "task_group_tasks": [{
              "title": "simple task 1",
              "description": self.generator.random_str(100)
            }, {
              "title": self.generator.random_str(),
              "description": self.generator.random_str(100)
            }, {
              "title": self.generator.random_str(),
              "description": self.generator.random_str(100)
            }
          ],
          "task_group_objects": self.random_objects
        }
      ]
    }
    self.one_time_workflow_2 = {
      "title": "test_wf_title",
      "description": "some test workflow",
      "task_groups": [{
        "title": "tg_1",
        "task_group_tasks": [{}, {}, {}]
      },
        {"title": "tg_2",
         "task_group_tasks": [{
           "description": self.generator.random_str(100)
            },
           {}
         ],
         "task_group_objects": self.random_objects[:2]
         },
        {"title": "tg_3",
         "task_group_tasks": [{
           "title": "simple task 1",
           "description": self.generator.random_str(100)
         }, {
           "title": self.generator.random_str(),
           "description": self.generator.random_str(100)
         }, {
           "title": self.generator.random_str(),
           "description": self.generator.random_str(100)
         }],
         "task_group_objects": []
         }
      ]
    }

    self.monthly_workflow_1 = {
      "title": "monthly test wf",
      "description": "start this many a time",
      "frequency": "monthly",
      "task_groups": [
        {"title": "tg_2",
         "task_group_tasks": [{
             "description": self.generator.random_str(100),
             "relative_end_day": 1,
             "relative_end_month": None,
             "relative_start_day": 5,
             "relative_start_month": None,
            },
            {"title": "monday task",
             "relative_end_day": 1,
             "relative_end_month": None,
             "relative_start_day": 1,
             "relative_start_month": None,
             },
            {"title": "weekend task",
             "relative_end_day": 4,
             "relative_end_month": None,
             "relative_start_day": 1,
             "relative_start_month": None,
             },
          ],
         "task_group_objects": self.random_objects
         },
      ]
    }

