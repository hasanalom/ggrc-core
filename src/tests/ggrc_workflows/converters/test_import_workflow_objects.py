# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: miha@reciprocitylabs.com
# Maintained By: miha@reciprocitylabs.com

from flask import json
from os.path import abspath
from os.path import dirname
from os.path import join

from tests.ggrc.converters import TestCase

from ggrc_workflows.models.task_group import TaskGroup
from ggrc_workflows.models.task_group_object import TaskGroupObject
from ggrc_workflows.models.task_group_task import TaskGroupTask
from ggrc_workflows.models.workflow import Workflow

THIS_ABS_PATH = abspath(dirname(__file__))


class TestWorkflowObjectsImport(TestCase):

  """
    Test imports for basic workflow objects
  """

  def setUp(self):
    TestCase.setUp(self)
    self.client.get("/login")
    self.CSV_DIR = join(THIS_ABS_PATH, "test_csvs/")

  def test_full_good_import_no_warnings(self):
    filename = "simple_workflow_test_no_warnings.csv"
    response = self.import_file(filename)
    messages = ("block_errors", "block_warnings", "row_errors", "row_warnings")

    broken_imports = set([
        "Control Assessment",
        "Task Group Task",
    ])

    for block in response:
      if block["name"] in broken_imports:
        continue
      for message in messages:
        self.assertEquals(set(), set(block[message]))

    self.assertEquals(1, Workflow.query.count())
    self.assertEquals(1, TaskGroup.query.count())
    self.assertEquals(1, TaskGroupTask.query.count())
    self.assertEquals(2, TaskGroupObject.query.count())
