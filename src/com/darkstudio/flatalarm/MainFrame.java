package com.darkstudio.flatalarm;

import java.awt.BorderLayout;
import java.awt.EventQueue;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JSeparator;
import javax.swing.JScrollPane;
import javax.swing.JToolBar;
import javax.swing.SwingConstants;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import com.darkstudio.flatalarm.ActionJList.EditorListener;

public class MainFrame implements ActionListener, ListSelectionListener, EditorListener<Alarm> {

    private static final String IC_ADD = "add.png";
    private static final String IC_EDIT = "edit.png";
    private static final String IC_DELETE = "delete.png";
    private static final String IC_START = "play.png";
    private static final String IC_STOP = "stop.png";
    private static final String IC_SETTINGS = "settings.png";
    private static final String IC_ABOUT = "about.png";
    private static final String IC_EXIT = "exit.png";

    private JFrame mainFrame;
    private ActionJList<Alarm> alarmList;
    private JButton editBtn;
    private JButton deleteBtn;
    private JButton startBtn;
    private JButton stopBtn;

    private AlarmManager mgr;

    /**
     * Launch the application.
     */
    public static void main(String[] args) {
        EventQueue.invokeLater(new Runnable() {
            public void run() {
                try {
                    MainFrame window = new MainFrame();
                    window.mainFrame.setVisible(true);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }

    /**
     * Create the application.
     */
    public MainFrame() {
        initialize();
    }

    /**
     * Initialize the contents of the frame.
     */
    private void initialize() {
        mainFrame = new JFrame();
        mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        mainFrame.setIconImage(Utils.getIconImage("app.png"));
        mainFrame.setTitle("Flat Alarm");
        mainFrame.setBounds(100, 100, 700, 400);

        JToolBar toolBar = new JToolBar();
        toolBar.setFloatable(false);
        mainFrame.getContentPane().add(toolBar, BorderLayout.NORTH);

        createToolbarButton(toolBar, IC_ADD, "Add a new alarm");
        editBtn = createToolbarButton(toolBar, IC_EDIT, "Edit selected alarm", false);
        deleteBtn = createToolbarButton(toolBar, IC_DELETE, "Delete selected alarm(s)", false);
        createToolbarSeparator(toolBar);
        startBtn = createToolbarButton(toolBar, IC_START, "Start selected alarm(s)", false);
        stopBtn = createToolbarButton(toolBar, IC_STOP, "Stop selected alarm(s)", false);
        createToolbarSeparator(toolBar);
        createToolbarButton(toolBar, IC_SETTINGS, "Global settings");
        createToolbarButton(toolBar, IC_ABOUT, "About Flat Alarm");
        createToolbarButton(toolBar, IC_EXIT, "Exit Flat Alarm");

        JScrollPane scrollPane = new JScrollPane();
        mainFrame.getContentPane().add(scrollPane, BorderLayout.CENTER);

        alarmList = new ActionJList<Alarm>(new DefaultListModel<Alarm>());
        alarmList.setCellRenderer(new AlarmCellRenderer());
        alarmList.setEditorListener(this);
        alarmList.addListSelectionListener(this);
        scrollPane.setViewportView(alarmList);

        mgr = new AlarmManager(alarmList);
    }

    private void createToolbarSeparator(JToolBar toolBar) {
        JSeparator sep = new JSeparator(SwingConstants.VERTICAL);
        toolBar.add(sep);
    }

    private JButton createToolbarButton(JToolBar toolBar, String ic_cmd, String tips) {
        return createToolbarButton(toolBar, ic_cmd, tips, true);
    }

    private JButton createToolbarButton(JToolBar toolBar, String ic_cmd, String tips, boolean enabled) {
        JButton btn = new JButton(Utils.getIcon(ic_cmd));
        btn.setToolTipText(tips);
        btn.setEnabled(enabled);
        btn.setActionCommand(ic_cmd);
        btn.addActionListener(this);
        toolBar.add(btn);
        return btn;
    }

    @Override
    public void actionPerformed(ActionEvent evt) {
        String cmd = evt.getActionCommand();
        switch (cmd) {
        case IC_ADD:
            addAlarm();
            break;

        case IC_EDIT:
            editAlarm();
            break;

        case IC_DELETE:
            deleteAlarm();
            break;

        case IC_START:
            switchAlarm(true);
            break;

        case IC_STOP:
            switchAlarm(false);
            break;

        case IC_SETTINGS:
            break;

        case IC_ABOUT:
            AboutDialog dlg = new AboutDialog(mainFrame);
            dlg.setLocationRelativeTo(mainFrame);
            dlg.setVisible(true);
            break;

        case IC_EXIT:
            mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            mainFrame.dispose();
            break;
        }
    }

    private void addAlarm() {
        AlarmEditDialog.newAlarm(mainFrame, mgr);
        mgr.showAlarms();
    }

    private void editAlarm() {
        Alarm alarm = mgr.getAlarm(alarmList.getSelectedIndex());
        AlarmEditDialog.editAlarm(mainFrame, mgr, alarm);
        mgr.showAlarms();
    }

    private void deleteAlarm() {
        mgr.deleteAlarms(alarmList.getSelectedIndices());
    }

    private void switchAlarm(boolean start) {
        int[] indices = alarmList.getSelectedIndices();
        if (Utils.isEmpty(indices)) {
            return;
        }
        for (int i = 0; i < indices.length; i++) {
            Alarm alarm = mgr.getAlarm(indices[i]);
            if (!alarm.isRunning() && start) {
                alarm.start();
            } else if (alarm.isRunning() && !start) {
                alarm.stop();
            }

        }
        mgr.showAlarms();
        updateStartStopButton(true, indices);
    }

    @Override
    public void valueChanged(ListSelectionEvent evt) {
        int[] indices = alarmList.getSelectedIndices();
        boolean selected = indices != null && indices.length > 0;

        editBtn.setEnabled(selected);
        deleteBtn.setEnabled(selected);

        updateStartStopButton(selected, indices);
    }

    private void updateStartStopButton(boolean selected, int[] indices) {
        if (!selected || Utils.isEmpty(indices)) {
            startBtn.setEnabled(false);
            stopBtn.setEnabled(false);
            return;
        }

        int running = 0;
        int nonrunning = 0;
        for (int i = 0; i < indices.length; i++) {
            Alarm alarm = mgr.getAlarm(indices[i]);
            if (alarm.isRunning()) {
                running++;
            } else {
                nonrunning++;
            }
        }

        startBtn.setEnabled(nonrunning > 0);
        stopBtn.setEnabled(running > 0);
    }

    @Override
    public void editingStopped(ActionJList<Alarm> list, int index, String value) {
        Alarm alarm = mgr.getAlarm(index);
        alarm.doInstruct(value);

        DefaultListModel<Alarm> model = (DefaultListModel<Alarm>) alarmList.getModel();
        model.set(index, alarm);
    }
}
