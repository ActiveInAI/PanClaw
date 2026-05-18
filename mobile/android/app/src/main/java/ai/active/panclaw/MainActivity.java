package ai.active.panclaw;

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(48, 64, 48, 48);

        TextView title = new TextView(this);
        title.setText("PanClaw");
        title.setTextSize(26);

        TextView body = new TextView(this);
        body.setText("OpenClaw, Hermes Agent, WeChat, WeCom, Feishu, Lark and DingTalk integration shell.");
        body.setTextSize(16);
        body.setPadding(0, 24, 0, 0);

        root.addView(title);
        root.addView(body);
        setContentView(root);
    }
}

