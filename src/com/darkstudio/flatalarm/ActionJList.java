package com.darkstudio.flatalarm;

import java.awt.Dimension;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.DefaultListModel;
import javax.swing.JList;
import javax.swing.JPopupMenu;
import javax.swing.JTextField;
import javax.swing.KeyStroke;
import javax.swing.ListModel;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;

/**
 * {@link JList} which select an item on double clicks or the ENTER key.
 */
@SuppressWarnings("serial")
public class ActionJList<E> extends JList<E> {

    private static final KeyStroke ENTER = KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, 0);

    public static final String ACTION_CMD = "ACTION_JLIST_CMD";

    private final Action editAction = new EditAction();

    private EditorListener<E> listener;

    public ActionJList(ListModel<E> model) {
        super(model);

        // Add the KeyStroke to the InputMap
        getInputMap().put(ENTER, ENTER);

        // Add the Action to the ActionMap
        getActionMap().put(ENTER, editAction);

        addMouseListener(new MouseAdapter() {
            public void mouseClicked(MouseEvent evt) {
                if (getSelectedValuesList().size() != 1 || evt.getClickCount() != 2) {
                    return;
                }

                Action action = getActionMap().get(ENTER);
                if (action != null) {
                    ActionEvent event = new ActionEvent(ActionJList.this,
                                                        ActionEvent.ACTION_PERFORMED, ACTION_CMD);
                    action.actionPerformed(event);
                }

                evt.consume();
            }
        });
    }

    public void setEditorListener(EditorListener<E> l) {
        listener = l;
    }

    public interface EditorListener<E> {
        public void editingStopped(ActionJList<E> list, int row, String value);
    }

    /**
     * A simple popup editor for a JList that allows you to change the value in the selected row.
     * <p>
     * The default implementation has a few limitations:
     * <p>
     * a) the JList must be using the DefaultListModel<br>
     * b) the data in the model is replaced with a String object
     * <p>
     * If you which to use a different model or different data then you must extend this class and:
     * <p>
     * a) invoke the setModelClass(...) method to specify the ListModel you need<br>
     * b) override the applyValueToModel(...) method to update the model
     */
    private class EditAction extends AbstractAction {

        private JPopupMenu editPopup;
        private JTextField editTextField;
        private Class<?> modelClass = DefaultListModel.class;

        public EditAction() {
        }

        @SuppressWarnings("unchecked")
        @Override
        public void actionPerformed(ActionEvent evt) {
            ActionJList<E> list = (ActionJList<E>) evt.getSource();
            ListModel<E> model = list.getModel();

            if (!modelClass.isAssignableFrom(model.getClass())) {
                return;
            }

            // Do a lazy creation of the popup editor
            if (editPopup == null) {
                createEditPopup(list);
            }

            // Position the popup editor over top of the selected row
            int row = list.getSelectedIndex();
            Rectangle r = list.getCellBounds(row, row);
            editPopup.setPreferredSize(new Dimension(r.width, r.height));
            editPopup.show(list, r.x, r.y);

            // Prepare the text field for editing
            editTextField.setText(list.getSelectedValue().toString());
            editTextField.selectAll();
            editTextField.requestFocusInWindow();
        }

        /**
         * Create the popup editor
         */
        private void createEditPopup(ActionJList<E> list) {
            // Use a text field as the editor
            editTextField = new JTextField();
            editTextField.setBorder(UIManager.getBorder("List.focusCellHighlightBorder"));

            // Add an Action to the text field to save the new value to the model
            editTextField.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent evt) {
                    if (listener != null) {
                        String value = editTextField.getText();
                        int row = list.getSelectedIndex();
                        listener.editingStopped(list, row, value);
                    }
                    editPopup.setVisible(false);
                }
            });

            // Add the editor to the popup
            editPopup = new JPopupMenu();
            editPopup.setBorder(new EmptyBorder(0, 0, 0, 0));
            editPopup.add(editTextField);
        }
    }
}
