// Altere a função para contar a história. Ela deve desenhar o quadro exato de t segundos.
window.drawMotion = (ctx, t, width, height) => {
  ctx.fillStyle = '#131929'; ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = '#70e0b3'; ctx.font = `bold ${Math.round(width * 0.085)}px sans-serif`;
  ctx.textAlign = 'center'; ctx.globalAlpha = Math.min(1, t * 2);
  ctx.fillText('Sua ideia em movimento', width / 2, height / 2, width * 0.86); ctx.globalAlpha = 1;
};
