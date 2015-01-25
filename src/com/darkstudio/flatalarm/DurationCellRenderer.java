package com.darkstudio.flatalarm;

import java.awt.Component;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JList;

@SuppressWarnings("serial")
public class DurationCellRenderer extends DefaultListCellRenderer {

    @Override
    public Component getListCellRendererComponent(JList<? extends Object> list, Object value,
            int index, boolean isSelected, boolean cellHasFocus) {
        Component c = super.getListCellRendererComponent(list, value, index, isSelected,
                                                         cellHasFocus);
        if (value instanceof Integer) {
            setText(Utils.formatDuration((Integer) value));
        }
        return c;
    }
}
