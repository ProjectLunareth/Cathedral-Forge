// /src/core/SacredGeometryCompiler.js

/**
 * The compiler, now evolved to understand the REPEL command.
 */
export class SacredGeometryCompiler {
  compile(dsl) {
    const layout = {
      steps: [],
      connections: [],
    };

    const commands = dsl.replace(/--.*$/gm, '').split(';').filter(cmd => cmd.trim() !== '');

    commands.forEach((commandStr, index) => {
      const trimmedCommand = commandStr.trim();
      const parts = trimmedCommand.match(/(?:[^\s"]+|"[^"]*")+/g) || [];
      if (parts.length === 0) return;

      const command = parts[0].toUpperCase();
      let step = { command, arguments: parts };

      try {
        switch (command) {
          case 'PLACE':
          case 'PULSE':
          case 'ORBIT':
          case 'ROTATE':
          case 'SCALE':
          case 'COLOR':
          case 'ATTRACT':
            layout.steps.push(step);
            break;
          
          case 'REPEL': { // New command
            const fromIndex = parts.indexOf('FROM');
            const strengthIndex = parts.indexOf('STRENGTH');
            if (fromIndex === -1 || strengthIndex === -1) {
              throw new Error('Invalid REPEL format. Use: REPEL "A" FROM "B" STRENGTH 1.0');
            }
            layout.steps.push(step);
            break;
          }

          case 'EMIT': {
            const fromIndex = parts.indexOf('FROM');
            if (fromIndex === -1) {
              throw new Error('Invalid EMIT format. Must include FROM "glyph_name".');
            }
            layout.steps.push(step);
            break;
          }

          case 'CONNECT': {
            const fromIndex = parts.indexOf('CONNECT') + 1;
            const toIndex = parts.indexOf('TO') + 1;
            if (toIndex === 0 || !parts[fromIndex] || !parts[toIndex]) {
              throw new Error('Invalid CONNECT format. Use: CONNECT "A" TO "B"');
            }
            const from = parts[fromIndex].replace(/"/g, '');
            const to = parts[toIndex].replace(/"/g, '');
            layout.connections.push({ from, to });
            break;
          }
          default:
            throw new Error(`Unknown command "${command}"`);
        }
      } catch(e) {
         throw new Error(`Syntax Error near command ${index + 1} ('${trimmedCommand}'): ${e.message}`);
      }
    });

    return layout;
  }
}
