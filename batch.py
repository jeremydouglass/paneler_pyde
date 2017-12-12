"""Manage batch processing of files with sources, filtered file lists and task queue."""
import os

class BatchProcess(object):
    """Manage a list of input and output files and/or folders
       which are passed to a process.
    """

    def __init__(self, process, **kwargs):
        self.cfg = {}
        self.process = process
        self.source_files = set()
        self.source_folders = set()
        self.source_trees = set()
        self.tasks = []
        self.errors = []
        self.template = {'path': '/data/templates', 'file' : 'gallery_css3.html'}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_tree_files(self, folder):
        """Add files recursively from a folder and subfolders."""
        files = self.list_tree(folder)
        for fname in files:
            if fname not in self.source_files:
                self.source_files.add(fname)

    def clear(self):
        """Clear source lists and current task queue."""
        self.clear_sources()
        self.clear_tasks()
        self.clear_errors()
        ## bump PDE console text
        for i in range(20):
            print '\n'

    def clear_errors(self):
        self.errors = []

    def clear_sources(self):
        """Clear source lists."""
        self.source_files = set()
        self.source_folders = set()
        self.source_trees = set()

    def clear_tasks(self):
        """Clear current task queue."""
        self.tasks = []

    def get_errors(self):
        result = []
        for error in self.errors:
            result.append(os.path.basename(error[0]) + ':\n   ' + str(error[1]) + '\n')
        return result
    
    def get_template(self):
        """Display template string in UI.
           Template is stored in a split relative directory
           and file name due convenience when working wtih
           the requirements of the Jinja2 API.
        """
        return [self.template['path'] + self.template['file']]

    @classmethod
    def list_tree(cls, folder, ext='.txt'):
        """Return a list of (matching) absolute paths for a folder
           and recursive subfolders.
        """
        results = []
        for root, folders, files in os.walk(folder): # pylint:disable = unused-variable
            for fname in files:
                if fname.endswith(ext):
                    results.append(os.path.join(root, fname))
        return results

    def next(self, **kwargs):
        """Process the next item in the tasks queue.
           Works like an iterator that can be reset.
        """
        if self.tasks:
            fname = self.tasks.pop(0)
            self.process(fname, **kwargs)

    def queue(self):
        """Resolve all source items and copy into tasks queue."""
        self.clear_errors()
        self.tasks = self.source_listing()

    def sources(self):
        """Display combined source lists."""
        result = []
        result.extend(self.source_files)
        result.extend(self.source_folders)
        result.extend(self.source_trees)
        return result

    def source_listing(self, ext='.txt'):
        """Realize task files from source lists, filtered by extension."""
        result = []
        for fname in self.source_files:
            if fname not in result:
                result.append(fname)
        for folder in self.source_folders:
            for fname in os.listdir(folder):
                result.append(fname)
        for tree in self.source_trees:
            for fname in self.list_tree(tree):
                result.append(fname)
        if ext:
            result = [item for item in result if item.endswith(ext)]
        return result

    def task_names(self):
        """Display short names of items in task queue."""
        return [os.path.basename(task) for task in self.tasks]
