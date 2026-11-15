// Adapt the preview daemon's Vite-style flags to Uvicorn.
import {spawn} from 'node:child_process';
const args=process.argv.slice(2);const option=(name,fallback)=>args.includes(name)?args[args.indexOf(name)+1]:fallback;
const child=spawn(process.env.PYTHON || 'python',['-m','uvicorn','backend.app:app','--host',option('--host','127.0.0.1'),'--port',option('--port','8000')],{stdio:'inherit'});
child.on('exit',code=>process.exit(code||0));process.on('SIGTERM',()=>child.kill('SIGTERM'));
