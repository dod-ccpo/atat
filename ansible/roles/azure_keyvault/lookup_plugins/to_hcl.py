# python 3 headers, required if submitting to Ansible
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
        lookup: file
        author: Daniel Hokka Zakrisson <daniel@hozac.com>
        version_added: "0.9"
        short_description: read file contents
        description:
            - This lookup returns the contents from a file on the Ansible controller's file system.
        options:
          _terms:
            description: path(s) of files to read
            required: True
        notes:
          - if read in variable context, the file can be interpreted as YAML if the content is valid to the parser.
          - this lookup does not understand globing --- use the fileglob lookup instead.
"""
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
import hcl

display = Display()


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):

        # lookups in general are expected to both take a list as input and output a list
        # this is done so they work with the looping construct 'with_'.

        ret = []
        for term in terms:
            display.debug("File lookup term: %s" % term)

            # Find the file in the expected search path, using a class method
            # that implements the 'expected' search path for Ansible plugins.
            lookupfile = self.find_file_in_search_path(variables, "files", term)

            # Don't use print or your own logging, the display class
            # takes care of it in a unified way.
            display.vvvv("File lookup using %s as file" % lookupfile)
            try:
                if lookupfile:
                    with open(term, "r") as fp:
                        obj = hcl.load(fp)

                        ret.append(obj)
                else:
                    # Always use ansible error classes to throw 'final' exceptions,
                    # so the Ansible engine will know how to deal with them.
                    # The Parser error indicates invalid options passed
                    raise AnsibleParserError()
            except AnsibleParserError:
                raise AnsibleError("could not locate file in lookup: %s" % term)

        return ret
