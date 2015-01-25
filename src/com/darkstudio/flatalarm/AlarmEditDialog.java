package com.darkstudio.flatalarm;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Rectangle;

import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import com.jgoodies.forms.layout.FormLayout;
import com.jgoodies.forms.layout.ColumnSpec;
import com.jgoodies.forms.layout.RowSpec;
import com.jgoodies.forms.factories.FormFactory;

import javax.swing.DefaultComboBoxModel;
import javax.swing.JLabel;
import javax.swing.JComboBox;
import javax.swing.JFormattedTextField;
import javax.swing.JOptionPane;
import javax.swing.JTextField;
import javax.swing.JCheckBox;
import javax.swing.BoxLayout;

@SuppressWarnings("serial")
public class AlarmEditDialog extends JDialog implements ActionListener {

    private static final String CMD_OK = "OK";
    private static final String CMD_CANCEL = "Cancel";

    private static final int WIDTH = 300;
    private static final int HEIGHT = 200;

    private static final DurationCellRenderer RENDER = new DurationCellRenderer();

    private static AlarmEditDialog dialog;

    private JFormattedTextField txtKickoff;
    private JCheckBox chkNow;
    private JComboBox<Integer> cmbDuration;
    private JComboBox<Integer> cmbRepeat;
    private JComboBox<String> cmbMessage;

    private AlarmManager mgr;
    private Alarm alarm;

    public static void newAlarm(Component parent, AlarmManager mgr) {
        editAlarm(parent, mgr, null);
    }

    public static void editAlarm(Component parent, AlarmManager mgr, Alarm alarm) {
        if (dialog == null) {
            dialog = new AlarmEditDialog(parent);
        }
        dialog.alarm = alarm;
        dialog.mgr = mgr;
        if (alarm != null) {
            dialog.bindAlarm(alarm);
        }
        dialog.setVisible(true);
    }

    /**
     * Create the dialog.
     */
    private AlarmEditDialog(Component parent) {
        super(JOptionPane.getFrameForComponent(parent));
        setModal(true);
        setModalityType(ModalityType.APPLICATION_MODAL);
        setTitle("Edit Alarm");
        setIconImage(Utils.getIconImage("app.png"));
        setMinimumSize(new Dimension(WIDTH, HEIGHT));
        setDefaultCloseOperation(HIDE_ON_CLOSE);

        Rectangle rect = parent.getBounds();
        setBounds(rect.x + (rect.width - WIDTH) / 2, rect.y + (rect.height - HEIGHT) / 2, WIDTH, HEIGHT);

        getContentPane().setLayout(new BorderLayout());

        JPanel contentPanel = new JPanel();
        contentPanel.setBorder(new EmptyBorder(5, 5, 5, 5));
        contentPanel.setLayout(new FormLayout(new ColumnSpec[] {ColumnSpec.decode("right:default"),
                                                                FormFactory.GROWING_BUTTON_COLSPEC,},
                                              new RowSpec[] {FormFactory.PREF_ROWSPEC,
                                                             FormFactory.PREF_ROWSPEC,
                                                             FormFactory.PREF_ROWSPEC,
                                                             FormFactory.PREF_ROWSPEC,}));
        getContentPane().add(contentPanel, BorderLayout.CENTER);

        contentPanel.add(new JLabel("Start time: "), "1, 1, right, default");
        contentPanel.add(new JLabel("Duration: "), "1, 2, right, default");
        contentPanel.add(new JLabel("Repeat: "), "1, 3, right, default");
        contentPanel.add(new JLabel("Message: "), "1, 4, right, default");

        txtKickoff = new JFormattedTextField();
        chkNow = new JCheckBox("now");

        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.X_AXIS));
        panel.add(txtKickoff);
        panel.add(chkNow);
        contentPanel.add(panel, "2, 1, fill, fill");

        cmbDuration = new JComboBox<Integer>();
        cmbDuration.setEditable(true);
        cmbDuration.setRenderer(RENDER);
        contentPanel.add(cmbDuration, "2, 2, fill, default");

        cmbRepeat = new JComboBox<Integer>();
        cmbRepeat.setEditable(true);
        cmbRepeat.setRenderer(RENDER);
        contentPanel.add(cmbRepeat, "2, 3, fill, default");

        cmbMessage = new JComboBox<String>();
        cmbMessage.setEditable(true);
        contentPanel.add(cmbMessage, "2, 4, fill, default");

        JPanel buttonPane = new JPanel();
        buttonPane.setLayout(new FlowLayout(FlowLayout.RIGHT));
        getContentPane().add(buttonPane, BorderLayout.SOUTH);

        JButton okBtn = new JButton(CMD_OK);
        okBtn.setActionCommand(CMD_OK);
        okBtn.addActionListener(this);
        buttonPane.add(okBtn);
        getRootPane().setDefaultButton(okBtn);

        JButton cancelBtn = new JButton(CMD_CANCEL);
        cancelBtn.setActionCommand(CMD_CANCEL);
        cancelBtn.addActionListener(this);
        buttonPane.add(cancelBtn);
    }

    private void bindAlarm(Alarm alarm) {
        // TODO Auto-generated method stub
        txtKickoff.setText(Utils.formatDateTime(alarm.getKickoff()));

        cmbDuration.setModel(new DefaultComboBoxModel<Integer>(mgr.getDurations()));
//        cmbDuration.getEditor().setItem(Utils.formatDuration(alarm.getDuration()));
        cmbDuration.setSelectedItem(alarm.getDuration());

        cmbRepeat.setModel(new DefaultComboBoxModel<Integer>(mgr.getRepeats()));
        int repeat = alarm.getRepeat();
        if (repeat > 0) {
            cmbRepeat.getEditor().setItem(Utils.formatDuration(repeat));
        } else {
            cmbRepeat.getEditor().setItem(repeat);
        }

        cmbMessage.setModel(new DefaultComboBoxModel<String>(mgr.getMessages()));
//        cmbMessage.getEditor().setItem(alarm.getMessage());
        cmbMessage.setSelectedItem(alarm.getMessage());
    }

    @Override
    public void actionPerformed(ActionEvent evt) {
        switch (evt.getActionCommand()) {
        case CMD_OK:
            break;

        case CMD_CANCEL:
            dispose();
            break;
        }
    }

}
