import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Coding {
	private static final int PORT = 8080;
	private static final Set<String> enrolledFaceFingerprints = new HashSet<>();
	private static final Pattern JSON_FIELD = Pattern.compile("\\\"%s\\\"\\s*:\\s*\\\"([^\\\"]*)\\\"");

	public static void main(String[] args) throws IOException {
		HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);
		server.createContext("/", Coding::handlePage);
		server.createContext("/api/enroll", Coding::handleEnrollment);
		server.setExecutor(null);
		server.start();
		System.out.println("Enrollment app running at http://localhost:" + PORT);
	}

	private static void handlePage(HttpExchange exchange) throws IOException {
		if (!"GET".equals(exchange.getRequestMethod())) {
			sendJson(exchange, 405, "{\"error\":\"Method not allowed\"}");
			return;
		}
		send(exchange, 200, "text/html; charset=UTF-8", HTML);
	}

	private static void handleEnrollment(HttpExchange exchange) throws IOException {
		if (!"POST".equals(exchange.getRequestMethod())) {
			sendJson(exchange, 405, "{\"error\":\"Method not allowed\"}");
			return;
		}

		String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
		String name = field(body, "name").trim();
		String ageText = field(body, "age").trim();
		String front = field(body, "front").trim();
		String left = field(body, "left").trim();
		String right = field(body, "right").trim();

		if (name.isBlank() || ageText.isBlank() || front.isBlank() || left.isBlank() || right.isBlank()) {
			sendJson(exchange, 400, "{\"error\":\"Name, age, and all three face captures are required.\"}");
			return;
		}

		int age;
		try {
			age = Integer.parseInt(ageText);
		} catch (NumberFormatException exception) {
			sendJson(exchange, 400, "{\"error\":\"Age must be a whole number.\"}");
			return;
		}
		if (age < 1 || age > 120) {
			sendJson(exchange, 400, "{\"error\":\"Age must be between 1 and 120.\"}");
			return;
		}

		String fingerprint = fingerprint(front, left, right);
		synchronized (enrolledFaceFingerprints) {
			if (enrolledFaceFingerprints.contains(fingerprint)) {
				sendJson(exchange, 409, "{\"error\":\"This face is already enrolled.\"}");
				return;
			}
			enrolledFaceFingerprints.add(fingerprint);
		}

		String response = "{\"id\":\"" + UUID.randomUUID() + "\",\"message\":\"Enrollment completed\"}";
		sendJson(exchange, 201, response);
	}

	private static String field(String json, String name) {
		Matcher matcher = Pattern.compile(String.format(JSON_FIELD.pattern(), Pattern.quote(name))).matcher(json);
		return matcher.find() ? matcher.group(1) : "";
	}

	private static String fingerprint(String... captures) {
		try {
			MessageDigest digest = MessageDigest.getInstance("SHA-256");
			for (String capture : captures) {
				digest.update(capture.replaceAll("\\s", "").getBytes(StandardCharsets.UTF_8));
			}
			return Base64.getEncoder().encodeToString(digest.digest());
		} catch (NoSuchAlgorithmException exception) {
			throw new IllegalStateException("SHA-256 is unavailable", exception);
		}
	}

	private static void sendJson(HttpExchange exchange, int status, String body) throws IOException {
		send(exchange, status, "application/json; charset=UTF-8", body);
	}

	private static void send(HttpExchange exchange, int status, String contentType, String body) throws IOException {
		byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
		exchange.getResponseHeaders().set("Content-Type", contentType);
		exchange.getResponseHeaders().set("Cache-Control", "no-store");
		exchange.sendResponseHeaders(status, bytes.length);
		try (OutputStream output = exchange.getResponseBody()) {
			output.write(bytes);
		}
	}

	private static final String HTML = """
			<!doctype html>
			<html lang="en">
			<head>
			  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
			  <title>Identity enrollment</title>
			  <style>
				@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;700&display=swap');
				:root{--ink:#18231f;--muted:#68756f;--mint:#c8f2d8;--green:#147d51;--paper:#f5f4ed;--line:#d9dfd6;--danger:#ad443d}
				*{box-sizing:border-box}body{margin:0;color:var(--ink);background:radial-gradient(circle at 80% 5%,#e1f3dc 0,transparent 28%),var(--paper);font-family:'DM Sans',sans-serif}
				main{display:grid;grid-template-columns:minmax(310px,480px) minmax(320px,620px);gap:7vw;max-width:1160px;margin:auto;padding:8vh 28px;min-height:100vh;align-items:center}
				h1,h2{font-family:'Space Grotesk',sans-serif;margin:0}h1{font-size:clamp(2.5rem,5vw,5rem);line-height:.98;letter-spacing:-.07em;max-width:450px}h2{font-size:1.2rem}.eyebrow{color:var(--green);font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:.72rem;margin-bottom:18px}
				.intro{color:var(--muted);font-size:1.05rem;line-height:1.6;max-width:420px;margin:24px 0 38px}.steps{display:flex;gap:12px}.step{width:34px;height:34px;border:1px solid var(--line);display:grid;place-items:center;border-radius:50%;font-size:.8rem}.step.active{background:var(--ink);color:white;border-color:var(--ink)}
				.panel{background:#fff;border:1px solid var(--line);padding:30px;box-shadow:0 20px 60px #263d2c12}.field{margin-bottom:20px}label{display:block;font-size:.82rem;font-weight:700;margin-bottom:8px}input{width:100%;border:1px solid var(--line);padding:13px 14px;border-radius:7px;font:inherit;color:var(--ink);background:#fcfcf9}input:focus{outline:2px solid var(--mint);border-color:var(--green)}
				.camera{position:relative;overflow:hidden;background:#18231f;aspect-ratio:4/3;margin:22px 0 14px;border-radius:6px}.camera video{width:100%;height:100%;object-fit:cover;transform:scaleX(-1)}.camera canvas{display:none}.guide{position:absolute;inset:12% 26%;border:2px solid #d7f4df;border-radius:48% 48% 43% 43%;box-shadow:0 0 0 999px #18231f45;pointer-events:none}.angle{font-weight:700;color:var(--green)}.capture-meta{display:flex;justify-content:space-between;color:var(--muted);font-size:.86rem}.capture-list{display:flex;gap:8px;margin-top:15px}.capture-list span{flex:1;padding:8px 3px;text-align:center;border:1px solid var(--line);border-radius:5px;font-size:.72rem}.capture-list .done{background:var(--mint);border-color:#a9dbba;color:#155b39}
				button{border:0;border-radius:7px;padding:13px 17px;font:700 .9rem 'DM Sans';cursor:pointer}button.primary{width:100%;background:var(--ink);color:white;margin-top:12px}button.secondary{background:var(--mint);color:var(--ink)}button:disabled{opacity:.45;cursor:not-allowed}.error{color:var(--danger);font-size:.85rem;min-height:20px;margin-top:10px}.success{background:var(--mint);padding:16px;border-radius:6px;line-height:1.5;display:none}.hidden{display:none!important}
				@media(max-width:760px){main{display:block;padding:42px 18px}.intro{margin-bottom:25px}.panel{padding:22px;margin-top:35px}h1{font-size:3.2rem}}
			  </style>
			</head>
			<body><main><section><div class="eyebrow">Secure identity register</div><h1>Make your presence official.</h1><p class="intro">Create a verified profile with a few simple details and three camera angles. Your captures stay in this session for the demo.</p><div class="steps"><span class="step active">1</span><span class="step">2</span><span class="step">3</span></div></section>
			<section class="panel"><div id="formView"><h2>New enrollment</h2><p class="intro" style="font-size:.9rem;margin:8px 0 20px">Enter your details, then follow the camera prompts.</p><div class="field"><label for="name">Full name</label><input id="name" autocomplete="name" placeholder="e.g. Alex Morgan"></div><div class="field"><label for="age">Age</label><input id="age" type="number" min="1" max="120" placeholder="18"></div><div class="camera"><video id="video" autoplay muted playsinline></video><canvas id="canvas"></canvas><div class="guide"></div></div><div class="capture-meta"><span>Look <b class="angle" id="angle">straight ahead</b></span><span id="count">0 / 3 captured</span></div><div class="capture-list"><span id="front">Front</span><span id="left">Slight left</span><span id="right">Slight right</span></div><button class="secondary" id="capture" style="margin-top:18px;width:100%">Capture angle</button><p class="error" id="error"></p><button class="primary" id="submit" disabled>Complete enrollment</button></div><div class="success" id="success"></div></section></main>
			<script>
			  const video=document.querySelector('#video'),canvas=document.querySelector('#canvas'),capture=document.querySelector('#capture'),submit=document.querySelector('#submit'),error=document.querySelector('#error'),angle=document.querySelector('#angle'),count=document.querySelector('#count');
			  const order=['front','left','right'], captures={}; let current=0,stream;
			  async function startCamera(){try{stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'user',width:{ideal:1280}},audio:false});video.srcObject=stream}catch(e){error.textContent='Camera access is required. Check browser permissions and use HTTPS or localhost.';capture.disabled=true}}
			  function update(){angle.textContent=current===0?'straight ahead':current===1?'slightly left':'slightly right';count.textContent=Object.keys(captures).length+' / 3 captured';capture.textContent=current<3?'Capture angle':'Retake selected angle';submit.disabled=Object.keys(captures).length!==3;order.forEach(x=>document.querySelector('#'+x).classList.toggle('done',!!captures[x]))}
			  capture.onclick=()=>{if(current>=3)current=0;const key=order[current];canvas.width=video.videoWidth;canvas.height=video.videoHeight;canvas.getContext('2d').drawImage(video,0,0);captures[key]=canvas.toDataURL('image/jpeg',.82);current++;update()};
			  submit.onclick=async()=>{error.textContent='';submit.disabled=true;const response=await fetch('/api/enroll',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.querySelector('#name').value,age:document.querySelector('#age').value,...captures})});const data=await response.json();if(!response.ok){error.textContent=data.error;submit.disabled=false;return}if(stream)stream.getTracks().forEach(track=>track.stop());document.querySelector('#formView').classList.add('hidden');const success=document.querySelector('#success');success.style.display='block';success.innerHTML='<strong>Enrollment complete.</strong><br>Profile ID: '+data.id;};
			  update();startCamera();
			</script></body></html>
			""";
}
