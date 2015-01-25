package com.darkstudio.flatalarm;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;

public class Alarm implements Comparable<Alarm> {

    private static final DateFormat DT_FROM = new SimpleDateFormat("yyyyMMddHHmmss");

    public static final int UNKNOWN = 0;
    public static final int RUNNING = 1;
    public static final int STOPPED = 2;
    public static final int EXPIRED = 3;

    private static final String[] STATUS_TXT = new String[] {
            "UNKNOWN", "RUNNING", "STOPPED", "EXPIRED"
    };

    private Calendar kickoff;
    private Calendar deadline;
    private String message;
    private int repeat; // in seconds
    private int duration; // in seconds
    private boolean running;

    private Alarm() {
    }

    public Calendar getKickoff() {
        return kickoff;
    }

    public void setKickoff(Calendar time) {
        kickoff = time;
    }

    public Calendar getDeadline() {
        return deadline;
    }

    public void setDeadline(Calendar time) {
        deadline = time;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String msg) {
        message = msg;
    }

    public int getRepeat() {
        return repeat;
    }

    public void setRepeat(int seconds) {
        repeat = seconds;
    }

    public int getDuration() {
        return duration;
    }

    public void setDuration(int seconds) {
        duration = seconds;
    }

    public void start() {
        running = true;
    }

    public void stop() {
        running = false;
    }

    public boolean isRunning() {
        return running;
    }

    public boolean isExpired() {
        if (deadline == null) {
            return false;
        }
        return !deadline.before(Calendar.getInstance());
    }

    public static Alarm parse(String l) {
        if (l == null || l.length() == 0) {
            return null;
        }
        l = l.trim();
        if (l.length() == 0) {
            return null;
        }

        Alarm alarm = new Alarm();

        // line format: kickoff;repeat;duration;running;message
        String[] parts = l.split(";");

        alarm.repeat = Integer.parseInt(parts[1]);
        alarm.duration = Integer.parseInt(parts[2]);
        alarm.running = (Integer.parseInt(parts[3]) == 1);
        alarm.message = parts[4];

        alarm.kickoff = Calendar.getInstance();
        alarm.deadline = Calendar.getInstance();
        try {
            alarm.kickoff.setTime(DT_FROM.parse(parts[0]));
            alarm.deadline.setTime(alarm.kickoff.getTime());
            alarm.deadline.add(Calendar.SECOND, alarm.duration);
        } catch (ParseException e) {
            e.printStackTrace();
            alarm.kickoff = null;
            alarm.deadline = null;
        }

        return alarm;
    }

    public String getStorageLine() {
        StringBuffer buf = new StringBuffer();
        buf.append(DT_FROM.format(kickoff.getTime())).append(';');
        buf.append(repeat).append(';');
        buf.append(duration).append(';');
        buf.append(running ? 1 : 0).append(';');
        buf.append(message);
        return buf.toString();
    }

    private String getRepeatString() {
        if (repeat == 0) {
            return "";
        }
        return "@ " + Utils.formatDuration(repeat);
    }

    public String getTimeInfo() {
        return String.format("%s <- %s (%s) %s", Utils.formatDateTime(deadline),
                             Utils.formatDateTime(kickoff), Utils.formatDuration(duration),
                             getRepeatString());
    }

    public int getStatus() {
        if (isExpired()) {
            return EXPIRED;
        }
        return running ? RUNNING : STOPPED;
    }

    @Override
    public String toString() {
        return String.format("%s : %s", Utils.formatDateTime(deadline), message);
    }

    @Override
    public int hashCode() {
        return deadline.hashCode() + message.hashCode();
    }

    public boolean equals(Object obj) {
        if (obj == null || !(obj instanceof Alarm)) {
            return false;
        }
        Alarm other = (Alarm) obj;
        return other.repeat == repeat && other.kickoff.equals(kickoff)
               && other.deadline.equals(deadline) && other.message.equals(message)
               && other.duration == duration;
    }

    @Override
    public int compareTo(Alarm other) {
        int compare = deadline.compareTo(other.deadline);
        if (compare != 0) {
            return compare;
        }
        compare = message.compareTo(other.message);
        if (compare != 0) {
            return compare;
        }
        if (repeat != other.repeat) {
            return repeat - other.repeat;
        }
        if (duration != other.duration) {
            return duration - other.duration;
        }
        return kickoff.compareTo(other.kickoff);
    }

    /**
     * Update {@code Alarm} with specified instruction
     * @param instruct the instruction to execute.
     */
    public void doInstruct(String instruct) {
        // TODO Auto-generated method stub

    }
}
