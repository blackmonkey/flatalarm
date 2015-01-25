package com.darkstudio.flatalarm;

import java.io.IOException;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Vector;

import javax.swing.DefaultListModel;
import javax.swing.JList;

public class AlarmManager {

    private static final String STORE_FILE = "alarms.txt";

    private ArrayList<Alarm> alarms = new ArrayList<Alarm>();
    private HashSet<Integer> durations = new HashSet<Integer>();
    private HashSet<Integer> repeats = new HashSet<Integer>();
    private HashSet<String> messages = new HashSet<String>();
    private JList<Alarm> alarmList;
    private Path storage;

    public AlarmManager(JList<Alarm> list) {
        alarmList = list;
        loadAlarms();
        showAlarms();
    }

    private void loadAlarms() {
        storage = Paths.get(Utils.getCurrentDir(), STORE_FILE);
        boolean opened = true;
        try {
            // create the file if it doesn't exist.
            Files.createFile(storage);
        } catch (FileAlreadyExistsException e) {
            // ignore
        } catch (IOException e) {
            e.printStackTrace();
            opened = false;
        }

        if (opened) {
            try {
                List<String> lines = Files.readAllLines(storage);
                parseStorage(lines);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private void parseStorage(List<String> lines) {
        alarms.clear();

        if (lines.size() == 0) {
            return;
        }

        for (String l : lines) {
            Alarm alarm = Alarm.parse(l);
            if (alarm != null) {
                alarms.add(alarm);
                durations.add(alarm.getDuration());
                repeats.add(alarm.getRepeat());
                messages.add(alarm.getMessage());
            }
        }

        alarms.sort(null);
    }

    public void showAlarms() {
        List<Alarm> selected = alarmList.getSelectedValuesList();
        ArrayList<Integer> indices = new ArrayList<Integer>(selected.size());

        DefaultListModel<Alarm> model = (DefaultListModel<Alarm>) alarmList.getModel();
        model.clear();
        for (int i = 0; i < alarms.size(); i++) {
            Alarm alarm = alarms.get(i);
            model.addElement(alarm);
            if (selected.contains(alarm)) {
                indices.add(i);
            }
        }

        int[] inds = new int[indices.size()];
        for (int i = 0; i < indices.size(); i++) {
            inds[i] = indices.get(i);
        }
        alarmList.setSelectedIndices(inds);
    }

    public void save() {
        Vector<String> lines = new Vector<String>();
        for (Alarm alarm : alarms) {
            lines.add(alarm.getStorageLine());
        }
        try {
            Files.write(storage, lines);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public Alarm getAlarm(int index) {
        return alarms.get(index);
    }

    public void deleteAlarms(int[] indices) {
        if (Utils.isEmpty(indices)) {
            return;
        }
        DefaultListModel<Alarm> model = (DefaultListModel<Alarm>) alarmList.getModel();
        for (int i = indices.length - 1; i >= 0; i--) {
            alarms.remove(indices[i]);
            model.remove(indices[i]);
        }
    }

    public Integer[] getDurations() {
        Integer[] res = new Integer[durations.size()];
        return durations.toArray(res);
    }

    public Integer[] getRepeats() {
        Integer[] res = new Integer[repeats.size()];
        return repeats.toArray(res);
    }

    public String[] getMessages() {
        String[] res = new String[messages.size()];
        return messages.toArray(res);
    }
}
