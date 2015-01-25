package com.darkstudio.flatalarm;

import java.awt.Image;
import java.awt.Toolkit;
import java.net.URL;
import java.nio.file.Paths;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;

import javax.swing.Icon;
import javax.swing.ImageIcon;

public class Utils {

    private static final String ICON_PATH = "/com/darkstudio/flatalarm/icons/";

    /**
     * <p>
     * <code>Utils</code> instances should NOT be constructed in standard programming.
     * <p>
     * Instead, the class should be used as:
     *
     * <pre>
     * Utils.escape(&quot;foo&quot;);
     * </pre>
     * <p>
     * This constructor is public to permit tools that require a JavaBean instance to operate.
     * </p>
     */
    public Utils() {
    }

    public static String getCurrentDir() {
        return Paths.get("").toAbsolutePath().toString();
    }

    public static String formatDateTime(Calendar time) {
        if (time == null) {
            return "";
        }
        DateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm");
        return df.format(time.getTime());
    }

    public static String formatDuration(int seconds) {
        if (seconds == 0) {
            return "";
        }

        int days = seconds / 86400;
        int hours = (seconds % 86400) / 3600;
        int mins = (seconds % 3600) / 60;
        int secs = seconds % 60;

        StringBuffer buf = new StringBuffer();
        if (days > 0) {
            buf.append(days).append("d ");
        }
        if (hours > 0) {
            buf.append(hours).append("h ");
        }
        if (mins > 0) {
            buf.append(mins).append("m ");
        }
        if (secs > 0) {
            buf.append(secs).append("s ");
        }
        buf.setLength(buf.length() - 1); // trim
        return buf.toString();
    }

    public static URL getIconUrl(String iconName) {
        return Utils.class.getResource(ICON_PATH + iconName);
    }

    public static Image getIconImage(String iconName) {
        return Toolkit.getDefaultToolkit().getImage(getIconUrl(iconName));
    }

    public static Icon getIcon(String iconName) {
        return new ImageIcon(getIconUrl(iconName));
    }

    public static boolean isEmpty(int[] ary) {
        return ary == null || ary.length == 0;
    }

    public static boolean isEmpty(String txt) {
        return txt == null || txt.length() == 0;
    }
}
