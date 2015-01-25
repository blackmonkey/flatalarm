package com.darkstudio.flatalarm;

import java.awt.Color;
import java.awt.Component;

import javax.swing.BorderFactory;
import javax.swing.DefaultListCellRenderer;
import javax.swing.JList;

@SuppressWarnings("serial")
public class AlarmCellRenderer extends DefaultListCellRenderer {

    @Override
    public Component getListCellRendererComponent(JList<? extends Object> list, Object value,
            int index, boolean isSelected, boolean cellHasFocus) {
        Component c = super.getListCellRendererComponent(list, value, index, isSelected,
                                                         cellHasFocus);

        if (value instanceof Alarm) {
            AlarmCellPanel panel = new AlarmCellPanel((Alarm) value);
            panel.setBackground(getBackground());
            return panel;
        }

        setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, Color.LIGHT_GRAY));
        return c;
    }
}
