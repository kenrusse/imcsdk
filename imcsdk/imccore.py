# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License prop
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the ImcSdk Core classes.
"""

import logging

from . import imcgenutils
from . import imccoreutils

try:
    import xml.etree.cElementTree as Et
    from xml.etree.cElementTree import Element, SubElement
except ImportError:
    import cElementTree as Et
    from cElementTree import Element, SubElement

log = logging.getLogger('imc')


class ImcBase(object):
    """
    This class acts as the base class for ManagedObject, ExternalMethod
    and AbstractFilter and BaseObject classes.
    """

    def __init__(self, class_id):
        self._class_id = class_id
        self._child = []
        self._handle = None

    @property
    def child(self):
        """Getter Method of ImcBase Class"""
        return self._child

    @property
    def dirty_mask(self):
        """Getter Method of ImcBase Class"""
        return self._dirty_mask

    def get_class_id(self):
        return self._class_id

    def get_handle(self):
        return self._handle

    def child_add(self, obj):
        """Method adds the child managed object."""
        self._child.append(obj)

    def child_remove(self, obj):
        """Method removes the child managed object."""
        self._child.remove(obj)

    def child_count(self):
        """Method returns the child managed object count."""
        return len(self._child)

    def child_to_xml(self, xml_doc, option=None, cookie=None):
        """Method writes the xml representation for the object."""
        for child in self._child:
            child.to_xml(xml_doc, option, cookie=cookie)

    def child_is_dirty(self):
        """Method checks whether the child object is dirty or not."""
        for child in self._child:
            if child.is_dirty():
                return True
        return False

    def child_mark_clean(self):
        """Method Method cleans the dirty mask of child managed object."""
        for child in self._child:
            child.mark_clean()

    def mark_clean(self):
        """Method cleans the dirty mask of the managed object."""
        self._dirty_mask = 0

    def is_dirty(self):
        """Method checks whether the object is dirty or not."""
        return self.child_is_dirty()

    def write_object(self):
        """Method writes the string representation of the object."""
        for child in self._child:
            if child:
                child.write_object()

    def clone(self):
        """ Method returns the clone of the Managed Object. """
        import copy

        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        """ Overridden method to support deepcopy of Managed Object. """
        import copy

        clone = copy.copy(self)
        clone_child = []
        for child in clone._child:
            clone_child.append(copy.deepcopy(child))
        clone._child = clone_child
        return clone

    def attr_set(self, key, value):
        """This method sets attribute value of the Method object."""
        self.__dict__[key] = value

    def attr_get(self, key):
        """This method gets attribute value of the Method object."""
        return self.__dict__[key]

    def elem_create(self, class_tag, xml_doc=None, override_tag=None):
        if xml_doc is None:
            xml_obj = Element(class_tag)
        else:
            if override_tag:
                xml_obj = SubElement(xml_doc, override_tag)
            else:
                xml_obj = SubElement(xml_doc, class_tag)
        return xml_obj


class AbstractFilter(ImcBase):
    """class AbstractFilter."""

    def __init__(self, class_id, tag_name=None):
        self._tag_name = tag_name
        ImcBase.__init__(self, class_id)

    def to_xml(self, xml_doc=None, option=None, elem_name=None, cookie=None):
        """This method writes the xml representation of the Method object."""
        xml_obj = self.elem_create(class_tag=self._tag_name,
                                   xml_doc=xml_doc,
                                   override_tag=elem_name)
        for key in self.__dict__:
            if key.startswith("_"):
                continue
            elif key == "class_":
                xml_obj.set("class", self.attr_get(key))
            else:
                xml_obj.set(key, self.attr_get(key))

        self.child_to_xml(xml_obj, option)
        return xml_obj


class BaseObject(ImcBase):
    """class BaseObject."""

    def __init__(self, class_id, tag_name=None):
        self._tag_name = tag_name
        ImcBase.__init__(self, class_id)

    def to_xml(self, xml_doc=None, option=None, elem_name=None, cookie=None):
        """This method writes the xml representation of the Method object."""
        xml_obj = self.elem_create(class_tag=self._tag_name,
                                   xml_doc=xml_doc,
                                   override_tag=elem_name)
        for key in self.__dict__:
            if key.startswith("_"):
                continue
            else:
                xml_obj.set(key, self.attr_get(key))

        self.child_to_xml(xml_obj, option, cookie=cookie)
        return xml_obj

    def from_xml(self, elem, handle=None):
        """This method creates the object from the xml representation
        of the Method object."""

        self._handle = handle
        if elem.attrib:
            for attr_name, attr_value in list(elem.attrib.items()):
                self.attr_set(imcgenutils.convert_to_python_var_name(attr_name),
                              str(attr_value))

        child_elems = elem.getchildren()
        if child_elems:
            for child_elem in child_elems:
                if not Et.iselement(child_elem):
                    continue

                cln = imcgenutils.word_u(child_elem.tag)
                child = imccoreutils.get_imc_obj(cln, child_elem)
                self._child.append(child)
                if isinstance(child, OperationStatus):
                    continue
                child.from_xml(child_elem, handle)


class ImcErrorResponse(object):
    """class ImcErrorResponse."""

    def __init__(self, error_code=None, error_descr=None):
        self.error_code = error_code
        self.error_descr = error_descr


class ImcCustomMethod(ImcBase):
    """class ImcCustomMethod."""

    def __init__(self, class_id, tag_name=None):
        self._tag_name = tag_name
        ImcBase.__init__(self, class_id)


class OperationStatus(ImcCustomMethod):
    """class OperationStatus"""

    def __init__(self, **kwargs):
        ImcCustomMethod.__init__(self, "OperationStatus", "operationStatus")
        if kwargs:
            for n, v in list(kwargs.items()):
                self.attr_set(n, v)
