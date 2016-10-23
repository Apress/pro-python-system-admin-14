#!/usr/bin/env python

import sys
import logging
import time
import subprocess
import boto
import boto.ec2
from ConfigParser import SafeConfigParser
import MySQLdb
from datetime import datetime

CFG_FILE = 'backup.cfg'

class BackupManager:

    def __init__(self, cfg_file=CFG_FILE, logger=None):
        self.logger = logger
        self.config = SafeConfigParser()
        self.config.read(cfg_file)
        self.aws_access_key = boto.config.get('Credentials', 'aws_access_key_id')
        self.aws_secret_key = boto.config.get('Credentials', 'aws_secret_access_key')
        self.ec2conn = boto.ec2.connection.EC2Connection(self.aws_access_key, self.aws_secret_key)
        self.image = self.ec2conn.get_image(self.config.get('main', 'image_id'))
        self.volume = self.ec2conn.get_all_volumes([self.config.get('main', 'volume_id')])[0]
        self.reservation = None
        self.ssh_cmd = []


    def _init_remote_cmd_args(self):
        key_file = "%s/%s.pem" % (self.config.get('main', 'key_location'), self.config.get('main', 'key_name'))
        remote_user = 'root'
        remote_host = self.reservation.instances[0].public_dns_name
        #remote_host = 'ec2-174-129-144-95.compute-1.amazonaws.com'
        remote_resource = "%s@%s" % (remote_user, remote_host)
        self.ssh_cmd = ['ssh',
                        '-o', 'StrictHostKeyChecking=no',
                        '-i', key_file,
                        remote_resource]

    def _start_instance(self):
        self.logger.debug('Starting new instance...')
        self.reservation = self.image.run(key_name=self.config.get('main', 'key_name'),
                                          security_groups=[self.config.get('main', 'security_grp')],
                                          placement=self.volume.zone)
        instance = self.reservation.instances[0]
        while instance.state != u'running':
            time.sleep(60)
            instance.update()
            self.logger.debug("instance state: %s" % instance.state)
        self.logger.debug("Instance %s is running and available at %s" % (instance.id, instance.public_dns_name))

    def _attach_volume(self, volume=None):
        if not volume:
            volume_to_attach = self.volume
        else:
            volume_to_attach = volume
        instance_id = self.reservation.instances[0].id
        self.logger.debug("Attaching volume %s to instance %s as %s" % (volume_to_attach.id, 
                                                                        instance_id, 
                                                                        self.config.get('main', 'vol_device')))
        volume_to_attach.attach(instance_id, self.config.get('main', 'vol_device'))
        while volume_to_attach.attachment_state() != u'attached':
            time.sleep(20)
            volume_to_attach.update()
            self.logger.debug("volume status: %s", volume_to_attach.attachment_state())
        time.sleep(10) # give it some extra time, aws sometimes is mis-reporting the volume state
        self.logger.debug("Finished attaching volume")


    def _detach_volume(self, volume=None):
        if not volume:
            volume_to_detach = self.volume
        else:
            volume_to_detach = volume
        self.logger.debug("Detaching volume %s" % volume_to_detach.id)
        volume_to_detach.detach()
        while volume_to_detach.attachment_state() == u'attached':
            time.sleep(20)
            volume_to_detach.update()
            self.logger.debug("volume status: %s", volume_to_detach.attachment_state())
        self.logger.debug('done')


    def _mount_volume(self):
        self.logger.debug("Mounting %s on %s" % (self.config.get('main', 'vol_device'),
                                                 self.config.get('main', 'mount_dir')))
        remote_command = "mount %(dev)s %(mp)s && df -h %(mp)s" % {'dev': self.config.get('main', 'vol_device'), 
                                                                  'mp': self.config.get('main', 'mount_dir')}
        rc = subprocess.call(self.ssh_cmd + [remote_command])
        self.logger.debug('done')

    def _copy_db(self):
        self.logger.debug('Backing up the DB...')
        time.sleep(60)
        #for i in range(5):
        #    self.logger.debug("%d minute(s) left" % (5-i))
        #    time.sleep(60)
    
    def _control_mysql(self, command):
        self.logger.debug("Sending MySQL DB daemon command to: %s" % command)
        remote_command = "/sbin/service mysqld %s; pgrep mysqld" % command
        rc = subprocess.call(self.ssh_cmd + [remote_command])
        self.logger.debug('done')


    def _unmount_volume(self):
        self.logger.debug("Unmounting %s" % self.config.get('main', 'mount_dir'))
        remote_command = "sync; sync; umount %(mp)s; df -h %(mp)s" % {'mp':self.config.get('main', 'mount_dir')}
        rc = subprocess.call(self.ssh_cmd + [remote_command])
        self.logger.debug('done')


    def _create_snapshot(self, volume=None):
        if not volume:
            volume_to_snapshot = self.volume
        else:
            volume_to_snapshot = volume
        self.logger.debug("Taking a snapshot of %s" % volume_to_snapshot.id)
        volume_to_snapshot.create_snapshot(description="Snapshot created on %s" % datetime.isoformat(datetime.now()))
        self.logger.debug('done')

    def _terminate_instance(self):
        instance = self.reservation.instances[0]
        self.logger.debug("Terminating instance %s" % instance.id)
        instance.stop()
        while instance.state != u'terminated':
            time.sleep(60)
            instance.update()
            self.logger.debug("instance state: %s" % instance.state)
        self.logger.debug('done')
        
        
def main():
    console = logging.StreamHandler()
    logger = logging.getLogger('DB_Backup')
    logger.addHandler(console)
    logger.setLevel(logging.DEBUG)
    bck = BackupManager(logger=logger)
    bck._start_instance()
    bck._init_remote_cmd_args()
    bck._attach_volume()
    bck._mount_volume()
    bck._control_mysql('start')
    bck._copy_db()
    bck._control_mysql('stop')
    bck._unmount_volume()
    bck._detach_volume()
    bck._create_snapshot()
    bck._terminate_instance()



if __name__ == '__main__':
    main()
