package com.darkstudio.flatalarm;

import com.jgoodies.forms.layout.FormLayout;
import com.jgoodies.forms.layout.ColumnSpec;
import com.jgoodies.forms.layout.RowSpec;
import com.jgoodies.forms.factories.FormFactory;

import java.awt.Font;
import java.awt.Color;
import java.awt.LayoutManager;

import javax.swing.BorderFactory;
import javax.swing.Icon;
import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;
import javax.swing.border.MatteBorder;
import javax.swing.UIManager;

@SuppressWarnings("serial")
public class AlarmCellPanel extends JPanel {

    private static final Color SEPARATOR_COLOR = UIManager.getColor("Label.background");
    private static final Border SPEARATOR_BORDER =
            BorderFactory.createCompoundBorder(new MatteBorder(0, 0, 1, 0, SEPARATOR_COLOR),
                                               new EmptyBorder(5, 5, 5, 5));
    private static final LayoutManager PANEL_LAYOUT =
            new FormLayout(new ColumnSpec[] {FormFactory.GROWING_BUTTON_COLSPEC, FormFactory.DEFAULT_COLSPEC,},
                           new RowSpec[] {FormFactory.PREF_ROWSPEC, FormFactory.PREF_ROWSPEC,});
    private static final Font TIME_FONT = new Font("Verdana", Font.BOLD, 12);
    private static final Font MSG_FONT = new Font(null, Font.PLAIN, 12);

    private static final Icon CHECK = Utils.getIcon("check.png");
    private static final Icon STOPPED = Utils.getIcon("stopped.png");
    private static final Icon RUNNING = Utils.getIcon("running.png");
    private static final Icon HELP = Utils.getIcon("help.png");

    /**
     * Create the panel.
     */
    public AlarmCellPanel(Alarm alarm) {
        setBorder(SPEARATOR_BORDER);
        setLayout(PANEL_LAYOUT);

        JLabel lblTime = new JLabel(alarm.getTimeInfo());
        lblTime.setFont(TIME_FONT);
        add(lblTime, "1, 1");

        JLabel lblRunning = new JLabel();
        switch (alarm.getStatus()) {
        case Alarm.RUNNING:
            lblRunning.setIcon(RUNNING);
            break;
        case Alarm.STOPPED:
            lblRunning.setIcon(STOPPED);
            break;
        case Alarm.EXPIRED:
            lblRunning.setIcon(CHECK);
            break;
        default:
            lblRunning.setIcon(HELP);
            break;
        }
        add(lblRunning, "2, 1, 1, 2");

        JLabel lblMessage = new JLabel(alarm.getMessage());
        lblMessage.setFont(MSG_FONT);
        add(lblMessage, "1, 2");
    }
}
