# Tachyon - Fast Multi-Threaded Web Discovery Tool
# Copyright (c) 2011 Gabriel Tremblay - initnull hat gmail.com
#
# GNU General Public Licence (GPL)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#

import re
from core import conf, utils, database
from core.fetcher import Fetcher
from urlparse import urljoin

def execute():
    """ Fetch /robots.txt and add the disallowed paths as target """
    worker_template = {'url': '', 'expected_response': [200, 302], 'timeout_count': 0, 'description': 'Robots.txt entry'}
    target_url = urljoin(conf.target_host, "/robots.txt")
    fetcher = Fetcher()
    response_code, content, headers = fetcher.fetch_url(target_url, 'GET', conf.user_agent, True, conf.fetch_timeout_secs)

    if response_code is 200 or response_code is 302 and content:
        if conf.debug:
            utils.output_debug(content)

        match = re.findall(r'Disallow:\s*[a-zA-Z0-9-/.]*', content)
        added = 0
        for match_obj in match:
            if '?' not in match_obj and '.' not in match_obj:                
                splitted = match_obj.split(':')
                if splitted[1]:
                    path = splitted[1].strip() 
                    if path != '/' or path != '':
                        new_path = urljoin(conf.target_host, path)
                        current_template = dict(worker_template)
                        current_template['url'] = new_path
                        database.paths.append(current_template)
        
                        if conf.debug:
                            utils.output_debug(str(current_template))
                            
                        added += 1
                    
        if added > 0:
            utils.output_info('Robots plugin: added ' + str(added) + ' base paths using /robots.txt')
        else :
            utils.output_info('Robots plugin: no usable entries in /robots.txt')     
               
    else:
        utils.output_info('Robots plugin: /robots.txt not found on target site')

