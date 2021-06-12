import os

import maya.OpenMayaUI as omui
import pymel.core as pm
import shiboken2
from PySide2 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

obj = shiboken2.wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)

import face.modules.build_rig_delete
reload(face.modules.build_rig_delete)

from lib import template_face
reload(template_face)
import pickle


class UI(MayaQWidgetBaseMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UI, self).__init__(parent=parent)

        # self.setWindowFlags(QtCore.Qt.Popup)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(5)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        self.setWindowTitle('ab_Facial_V 0.1')
        self.setGeometry(100, 100, 250, 300)

        ## tab
        tab = QtWidgets.QTabWidget()
        geo_widget = QtWidgets.QWidget()
        template_widget = QtWidgets.QWidget()
        rig_widget = QtWidgets.QWidget()
        tab.addTab(geo_widget, 'Geo')
        tab.addTab(template_widget, 'Template')
        tab.addTab(rig_widget, 'Rig')
        self.layout().addWidget(tab)
        ##

        # geo
        geo_widget.setLayout(QtWidgets.QVBoxLayout())
        geo_frame = QtWidgets.QFrame()
        geo_frame.setFrameStyle(QtWidgets.QFrame.Box)
        geo_frame.setLayout(QtWidgets.QGridLayout())
        geo_widget.layout().addWidget(geo_frame)

        head = QtWidgets.QLabel('Head:')
        l_eye = QtWidgets.QLabel('L_Eye:')
        r_eye = QtWidgets.QLabel('R_Eye:')
        brow = QtWidgets.QLabel('Brow:')

        self.head_geo = QtWidgets.QLineEdit()
        self.head_geo.setPlaceholderText('head_geo')
        self.l_eye_geo = QtWidgets.QLineEdit()
        self.l_eye_geo.setPlaceholderText('L_eye_geo')
        self.r_eye_geo = QtWidgets.QLineEdit()
        self.r_eye_geo.setPlaceholderText('R_eye_geo')
        self.brow_geo = QtWidgets.QLineEdit()
        self.brow_geo.setPlaceholderText('brow_geo')

        self.head_edit = QtWidgets.QPushButton('<<')
        self.head_edit.setMaximumWidth(30)
        self.l_eye_edit = QtWidgets.QPushButton('<<')
        self.l_eye_edit.setMaximumWidth(30)
        self.r_eye_edit = QtWidgets.QPushButton('<<')
        self.r_eye_edit.setMaximumWidth(30)
        self.brow_edit = QtWidgets.QPushButton('<<')
        self.brow_edit.setMaximumWidth(30)

        self.head_edit.clicked.connect(self.connect_head_geo)
        self.l_eye_edit.clicked.connect(self.connect_l_eye_geo)
        self.r_eye_edit.clicked.connect(self.connect_r_eye_geo)
        self.brow_edit.clicked.connect(self.connect_brow_geo)

        geo_frame.layout().addWidget(head, 0, 0)
        geo_frame.layout().addWidget(self.head_geo, 0, 1)
        geo_frame.layout().addWidget(self.head_edit, 0, 2)

        geo_frame.layout().addWidget(l_eye, 1, 0)
        geo_frame.layout().addWidget(self.l_eye_geo, 1, 1)
        geo_frame.layout().addWidget(self.l_eye_edit, 1, 2)

        geo_frame.layout().addWidget(r_eye, 2, 0)
        geo_frame.layout().addWidget(self.r_eye_geo, 2, 1)
        geo_frame.layout().addWidget(self.r_eye_edit, 2, 2)

        geo_frame.layout().addWidget(brow, 3, 0)
        geo_frame.layout().addWidget(self.brow_geo, 3, 1)
        geo_frame.layout().addWidget(self.brow_edit, 3, 2)

        # template_hold
        template_widget.setLayout(QtWidgets.QVBoxLayout())

        template_side_widget = QtWidgets.QWidget()
        template_side_widget.setLayout(QtWidgets.QHBoxLayout())
        template_side = QtWidgets.QLabel('Side : ')

        template_cb = QtWidgets.QComboBox()
        for each in ['L', 'R', 'All']:
            template_cb.addItem(each)
        template_side_widget.layout().addWidget(template_side)
        template_side_widget.layout().addWidget(template_cb)
        template_widget.layout().addWidget(template_side_widget)
        #

        up_lid = ModuleWidget('Up_Lid')
        template_widget.layout().addWidget(up_lid)

        lo_lid = ModuleWidget('Lo_Lid')
        template_widget.layout().addWidget(lo_lid)

        up_ring = ModuleWidget('Up_Ring')
        template_widget.layout().addWidget(up_ring)

        lo_ring = ModuleWidget('Lo_Ring')
        template_widget.layout().addWidget(lo_ring)

        brow = ModuleWidget('Brow')
        template_widget.layout().addWidget(brow)

        temp = TemplateWidget(up_lid, lo_lid, up_ring, lo_ring, brow, template_cb, self)
        template_widget.layout().addWidget(temp)

        # rig
        rig_widget.setLayout(QtWidgets.QVBoxLayout())

        rig = RigWidget(self)
        rig_widget.layout().addWidget(rig)

        self.set_geos()

    def connect_head_geo(self):
        sel = pm.ls(sl=1)
        if sel:
            self.head_geo.setText(sel[0].name())

    def connect_l_eye_geo(self):
        sel = pm.ls(sl=1)
        if sel:
            self.l_eye_geo.setText(sel[0].name())

    def connect_r_eye_geo(self):
        sel = pm.ls(sl=1)
        if sel:
            self.r_eye_geo.setText(sel[0].name())

    def connect_brow_geo(self):
        sel = pm.ls(sl=1)
        if sel:
            self.brow_geo.setText(sel[0].name())

    def get_geos(self):
        return [self.head_geo.text(), self.l_eye_geo.text(), self.r_eye_geo.text(), self.brow_geo.text()]

    def set_geos(self):
        self.head_geo.setText('face_skin_localRig')
        self.l_eye_geo.setText('L_pupil_geo')
        self.r_eye_geo.setText('R_pupil_geo')
        self.brow_geo.setText('brow_geo1')


class ModuleWidget(QtWidgets.QFrame):
    def __init__(self, part):
        super(ModuleWidget, self).__init__()
        self.setMaximumSize(250, 300)

        # self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        self.edges = None

        self.setFrameStyle(QtWidgets.QFrame.Box)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.setLayout(layout)

        self.text = QtWidgets.QLabel('%s : ' % part)
        self.text.setMaximumWidth(50)
        self.text_box = QtWidgets.QLineEdit()
        self.text_box.setMaximumWidth(150)
        self.text_box.setPlaceholderText('edgeLoop')
        self.btn = QtWidgets.QPushButton('<<')
        self.btn.setMaximumWidth(30)

        layout.addWidget(self.text)
        layout.addWidget(self.text_box)
        layout.addWidget(self.btn)

        self.btn.clicked.connect(self.connect_btn)

    def connect_btn(self):
        # print self.text.text().split(':')[0]
        self.edges = pm.ls(sl=1)
        self.text_box.setText(str(self.edges))

    def get_edges(self):
        return self.edges


class TemplateWidget(QtWidgets.QFrame):
    def __init__(self, *args):
        super(TemplateWidget, self).__init__()
        self.setMaximumSize(250, 300)
        self.modules = args
        self.up_lid = self.modules[0]
        self.lo_lid = self.modules[1]

        self.up_ring = self.modules[2]
        self.lo_ring = self.modules[3]

        self.brow = self.modules[4]
        self.template_side = self.modules[5]

        self.geos = self.modules[6]

        self.mirror_data = None
        self.template_data = []

        self.setFrameStyle(QtWidgets.QFrame.Box)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        self.build = QtWidgets.QPushButton('Build')
        self.mirror = QtWidgets.QPushButton('Mirror')
        self.remove = QtWidgets.QPushButton('Delete')
        self.save = QtWidgets.QPushButton('Save')
        self.rebuild = QtWidgets.QPushButton('Import')

        layout.addWidget(self.build)
        layout.addWidget(self.mirror)
        layout.addWidget(self.remove)
        layout.addWidget(self.save)
        layout.addWidget(self.rebuild)

        self.build.clicked.connect(self.connect_build)
        self.mirror.clicked.connect(self.connect_mirror)
        self.remove.clicked.connect(self.connect_delete)
        self.save.clicked.connect(self.connect_save)
        self.rebuild.clicked.connect(self.connect_import)

    def connect_build(self):

        up_lid_edges = self.up_lid.get_edges()
        lo_lid_edges = self.lo_lid.get_edges()

        up_ring_edges = self.up_ring.get_edges()
        lo_ring_edges = self.lo_ring.get_edges()

        brow_edges = self.brow.get_edges()

        # main
        with UndoContext():
            lid_hold_inst = template_face.Template('M')
            lid_hold_inst.build_eye_hold()
            lid_hold_inst.build_brow_hold()
            self.template_data.append(lid_hold_inst)

            inst = template_face.Template(self.template_side.currentText())
            geos = self.geos.get_geos()
            for each in geos:
                if each.startswith(self.template_side.currentText()):
                    inst.build_eye_proxy(each)

            inst.build_up_lids_proxy(up_lid_edges)
            inst.build_lo_lids_proxy(lo_lid_edges)

            inst.build_up_ring_proxy(up_ring_edges)
            inst.build_lo_ring_proxy(lo_ring_edges)

            inst.build_brow_proxy(brow_edges)

            self.mirror_data = inst
            self.template_data.append(inst)

    def connect_mirror(self):
        with UndoContext():
            self.mirror_data.mirror()
            # self.mirror_data.export_template()
            self.save_instance()

    def connect_delete(self):
        with UndoContext():
            if self.template_side.currentText() == 'L':
                self.mirror_data.delete_template('R')
            elif self.template_side.currentText() == 'R':
                self.mirror_data.delete_template('L')
            else:
                return
            self.save_instance()

    def save_instance(self, path=None):
        data = {}
        for each in self.mirror_data.data.keys():
            data[each] = each
        # save
        if path:
            path = path
        else:
            path = pm.system.sceneName().dirname()

        file_name = os.path.join(path, '{}.{}'.format('datafile', 'txt'))
        with open(file_name, 'w') as fh:
            pickle.dump(self.template_data, fh)

    def connect_save(self):
        with UndoContext():
            a = self.template_data[0].data
            b = self.template_data[1].data
            main_data = a.copy()
            main_data.update(b)
            template_inst = template_face.Template('M')
            template_inst.export_template(main_data)
            self.save_instance()

    def connect_import(self, path=None):
        with UndoContext():
            template_inst = template_face.Template('M')
            template_inst.import_template()

            if len(self.template_data) == 0:
                if path:
                    path = path
                else:
                    path = pm.system.sceneName().dirname()

                file_name = os.path.join(path, '{}.{}'.format('datafile', 'txt'))
                with open(file_name) as fh:
                    inst_data = pickle.load(fh)

                self.template_data = inst_data
                self.mirror_data = inst_data[1]


class RigWidget(QtWidgets.QFrame):
    def __init__(self, rig_widget):
        super(RigWidget, self).__init__()
        self.setMaximumSize(250, 300)

        self.setFrameStyle(QtWidgets.QFrame.Box)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        self.rig_widget = rig_widget

        # sides
        side_widget = QtWidgets.QWidget()
        sides_layout = QtWidgets.QHBoxLayout()
        side_text = QtWidgets.QLabel('side :')
        self.sides_cb = QtWidgets.QComboBox()
        for each in ['LR', 'L', 'R', 'M', 'LMR']:
            self.sides_cb.addItem(each)
        sides_layout.addWidget(side_text)
        sides_layout.addWidget(self.sides_cb)
        side_widget.setLayout(sides_layout)
        self.layout().addWidget(side_widget)

        # check
        check_widget = QtWidgets.QWidget()
        check_layout = QtWidgets.QHBoxLayout()
        self.lid_check = QtWidgets.QCheckBox('Lid')
        self.lid_check.setChecked(True)
        self.ring_check = QtWidgets.QCheckBox('Ring')
        self.ring_check.setChecked(True)
        self.brow_check = QtWidgets.QCheckBox('Brow')
        self.brow_check.setChecked(True)
        self.eye_check = QtWidgets.QCheckBox('Eye')
        self.eye_check.setChecked(True)

        check_layout.addWidget(self.lid_check)
        check_layout.addWidget(self.ring_check)
        check_layout.addWidget(self.brow_check)
        check_layout.addWidget(self.eye_check)

        check_widget.setLayout(check_layout)
        self.layout().addWidget(check_widget)

        # rig
        rig_btn = QtWidgets.QPushButton('RIG')
        self.layout().addWidget(rig_btn)

        rig_btn.clicked.connect(self.connect_rig)

    def connect_rig(self):
        sides = self.sides_cb.currentText()
        lid = self.lid_check.isChecked()
        ring = self.ring_check.isChecked()
        brow = self.brow_check.isChecked()
        eye = self.eye_check.isChecked()

        with UndoContext():
            rig_inst = face.modules.build_rig_delete.RIG()
            geos = self.rig_widget.get_geos()
            rig_inst.first_layer(sides, geos[0], geos[1], geos[2], lid, ring, eye)

            if brow:
                rig_inst.second_layer(sides)
            rig_inst.bind_geo(*geos)


class UndoContext(object):
    def __enter__(self):
        pm.undoInfo(openChunk=True)

    def __exit__(self, *exc_info):
        pm.undoInfo(closeChunk=True)
