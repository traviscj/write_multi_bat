#!/usr/bin/env python

""" write_multi_bat: a python code to generate many .bat files from template.
"""

__author__ = "Travis C. Johnson"
__copyright__ = "Copyright 2013, Travis C. Johnson"
__credits__ = ["Travis C. Johnson", "Jonathan Beals"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Travis C. Johnson"
__email__ = "traviscj@traviscj.com"
__status__ = "Prototype"

from zipfile import ZipFile
from os import unlink
from tempfile import mkdtemp
from time import asctime

# This is the template for the .bat files.
# The {thing} things get filled in by magic later. I use r"string" (aka, a 
# regex string) to keep the backslashes literal--easy peasy!
template = r"""
REM Generated by write_multi_bat.py at {current_time}
"C:\Program Files\Autodesk\Maya2013\bin\Render.exe" -r arnold -rl shadow1 -s {start} -e {end} -ai:lfn C:\Users\jonathan\Desktop\renderlog_{proj}_{lognum}.log -rd {out} {infile}

pause
"""

class write_mult_bat(object):
    def __init__(self, project, input_file, output_directory, first, last, step):
        self.project = project
        self.input_file = input_file
        self.output_directory = output_directory
        self.first = first
        self.last = last
        self.step = step
        
    def render_data(self):
        """ render_data generates the data that goes into the .bat files, given
        the project name, input file for the renderer, and directory that the
        output should be stored. We also make use of the first/last/step params
        to decide when to start/stop.
        """

        i,result,curStart,curEnd=0,[],self.first,self.first+self.step
        while curEnd < self.last:
            curStart = self.first + self.step*i
            curEnd = min(self.first + self.step*(i+1)-1,self.last)

            # fill in the template information using this loop and the
            # information this function was passed:
            result.append(
                template.format(
                    start=curStart,
                    end=curEnd,
                    lognum=i,
                    proj=self.project,
                    infile=self.input_file,
                    out=self.output_directory,
                    current_time=asctime()
                    )
                )
                
            i += 1
        return result

    def render_files(self, renderfiles_list, bat_file_prefix):
        """ render_files takes a list of render files(the contents of the .bat
        files) and a prefix to use for the .bat files, and returns two lists:
        1) the list of filenames (relative to bat_file_prefix)
        2) the list of files with the prefix included.

        I return both so that the _zip function does not need to regenerate
        all of these full filenames. (Not that it's expensive to do so, but
        avoids needing to keep code in sync in two places.)
        """

        # these two store the filename and the full file paths, respectively
        # ie, beals_render.bat vs /tmp/XXX/beals_render.bat
        bat_file_list, bat_full_file_list = [], []

        # okay, for each .bat file contents
        for i,onebatcontents in enumerate(renderfiles_list):
            # this determines the filename of the .bat file
            fname = 'beals_render_{index}.bat'.format(index=i)

            # and this is the path of the .bat file, including the directory
            full_fname = '{tempdir}/{batfile}'.format(
                tempdir=bat_file_prefix,
                batfile=fname
                )

            # open and fill that file:
            f=open(full_fname,'w')
            f.write( onebatcontents )
            f.close()

            # and then add the filenames to the things we will return
            bat_file_list.append(fname)
            bat_full_file_list.append(full_fname)

        # finally, return it.
        return bat_file_list,bat_full_file_list
    def render_text(self):
        return "".join(self.render_data())
    def render_zip(self):
        """ render_zip takes project, input file, and output directory and 
        returns the name of a zipfile containing all of the .bat files to do
        that run.
        """
    
        # create a temporary directory to store our bat files:
        tempdir = mkdtemp(prefix='beals_render_')
    
        # ...then create a zipfile with that base name...
        zipf = "{0}/beals_render.zip".format(tempdir)
        with ZipFile(zipf, 'w') as myzip:
            # generate all data for the render files
            data_lst = self.render_data()
        
            # put the data into .bat files
            rf_list,rf_full_list = self.render_files(data_lst, tempdir)
        
            # for each .bat file:
            for batfile,fullbatfile in zip(rf_list,rf_full_list):
                # generate a name for the zip file,
                zipfile_bat_file_name = 'beals_render/{0}'.format(batfile)
                
                # put the file into the zip file,
                myzip.write(fullbatfile, arcname=zipfile_bat_file_name)
                
                # then delete it.
                unlink(fullbatfile)

        # Now return the filename of the zip file
        return zipf

if __name__ == "__main__":
    # THIS is where to change project names and files and output directories.
    wmb = write_mult_bat(
        r"paper_dancer",
        r"\\goliath\STORAGE1\prod\jobs\internal\paper_dancer\shots\dancer\010\components\light2\work\010_light2_work_0015.ma",
        r"\\goliath\STORAGE1\prod\jobs\internal\paper_dancer\maya\images",
        first=101,
        last=110,
        step=2
        )
    print(wmb.render_text())
    # zipfilename = wmb.render_zip();
    # print("Generated file was: {zipfile}".format(zipfile=zipfilename))
