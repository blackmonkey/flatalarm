package com.darkstudio.flatalarm;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;

@SuppressWarnings("serial")
public class AboutDialog extends JDialog implements ActionListener {

    private static final String CMD_OK = "OK";

    /**
     * Create the dialog.
     *
     * @param parent
     */
    public AboutDialog(JFrame parent) {
        super(parent);

        setModalityType(DEFAULT_MODALITY_TYPE);
        setResizable(false);
        setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
        setTitle(Messages.get("AboutDialog.Title"));
        setSize(360, 150);
        getContentPane().setLayout(null);

        JButton okButton = new JButton(Messages.get("AboutDialog.BtnOk"));
        okButton.setBounds(290, 10, 55, 23);
        okButton.setActionCommand(CMD_OK);
        okButton.addActionListener(this);
        getContentPane().add(okButton);
        getRootPane().setDefaultButton(okButton);

        JLabel lblName = new JLabel(Messages.get("AboutDialog.Software"));
        lblName.setBounds(10, 10, 270, 20);
        getContentPane().add(lblName);

        JLabel lblCopyright = new JLabel(Messages.get("AboutDialog.Copyright"));
        lblCopyright.setBounds(10, 30, 270, 20);
        getContentPane().add(lblCopyright);
    }

    @Override
    public void actionPerformed(ActionEvent evt) {
        if (CMD_OK.equals(evt.getActionCommand())) {
            dispose();
        }
    }
}
