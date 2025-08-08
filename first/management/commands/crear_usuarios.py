from django.core.management.base import BaseCommand
from first.models import Usuario, Ciudad

class Command(BaseCommand):
    help = 'Crea usuarios con contraseñas para el sistema de login'

    def handle(self, *args, **options):
        self.stdout.write('👥 Creando usuarios con contraseñas...')
        
        # Crear ciudad si no existe
        ciudad, created = Ciudad.objects.get_or_create(
            nombre="Buenos Aires",
            defaults={'codPostal': '1000'}
        )
        
        # Lista de usuarios a crear
        usuarios_data = [
            {
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'dni': 12345678,
                'telefono': '11-1234-5678',
                'password': 'admin123'
            },
            {
                'nombre': 'María',
                'apellido': 'González',
                'dni': 23456789,
                'telefono': '11-2345-6789',
                'password': 'admin123'
            },
            {
                'nombre': 'Carlos',
                'apellido': 'López',
                'dni': 34567890,
                'telefono': '11-3456-7890',
                'password': 'admin123'
            },
            {
                'nombre': 'Ana',
                'apellido': 'Martínez',
                'dni': 45678901,
                'telefono': '11-4567-8901',
                'password': 'admin123'
            },
            {
                'nombre': 'Luis',
                'apellido': 'Rodríguez',
                'dni': 56789012,
                'telefono': '11-5678-9012',
                'password': 'admin123'
            }
        ]
        
        usuarios_creados = 0
        
        for user_data in usuarios_data:
            try:
                usuario, created = Usuario.objects.get_or_create(
                    dni=user_data['dni'],
                    defaults={
                        'nombre': user_data['nombre'],
                        'apellido': user_data['apellido'],
                        'telefono': user_data['telefono'],
                        'is_active': True
                    }
                )
                
                if created:
                    # Establecer contraseña hasheada
                    usuario.set_password(user_data['password'])
                    usuario.save()
                    usuarios_creados += 1
                    self.stdout.write(f'✅ Usuario creado: {usuario.nombre} {usuario.apellido} (DNI: {usuario.dni})')
                else:
                    # Actualizar contraseña si el usuario ya existe
                    usuario.set_password(user_data['password'])
                    usuario.is_active = True
                    usuario.save()
                    self.stdout.write(f'🔄 Usuario actualizado: {usuario.nombre} {usuario.apellido} (DNI: {usuario.dni})')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error creando usuario {user_data["nombre"]}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'🎉 ¡Proceso completado! {usuarios_creados} usuarios creados/actualizados'))
        self.stdout.write('📝 Credenciales de acceso:')
        self.stdout.write('   Usuario: DNI del usuario')
        self.stdout.write('   Contraseña: admin123')
        self.stdout.write('')
        self.stdout.write('👤 Usuarios disponibles:')
        for user_data in usuarios_data:
            self.stdout.write(f'   - {user_data["nombre"]} {user_data["apellido"]} (DNI: {user_data["dni"]})') 