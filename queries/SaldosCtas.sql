select EntPar.codigo as titular, EntAdm.rut, EntPar.Nombre, EntPar.Apellidos , fon.fondo, fon.planes, par.secuencia, par.regimen_tributario, Cta.codigo as cuenta,   sal.participaciones SaldoCuota from 
                 PAR_SALDOS Sal
               , cuentas_tit Cta 
               , cuentas_par Par
               , cuentas_FON Fon
               , Entidades_ADM EntAdm
               , Entidades   Ent
               , Entidades   EntPar
where Ent.Codigo = Cta.Codigo
and   Par.Codigo = Cta.codigo
and   Sal.cuenta = Cta.Codigo
and   Fon.Cuenta = Cta.Codigo
and   Cta.titular >= 2962322 and Cta.titular <= 2962400
and   EntPar.codigo = Cta.titular
and   EntAdm.codigo = EntPar.codigo
order by EntPar.codigo
;
