import fs from 'fs';
import path from 'path';
import { graphSchema } from '../../app/src/lib/schemas';

const outputDir = path.join(__dirname, '../../dist/schemas');
fs.mkdirSync(outputDir, { recursive: true });
fs.writeFileSync(path.join(outputDir, 'project.schema.json'), JSON.stringify(graphSchema, null, 2));
console.log(`Schema written to ${outputDir}`);
